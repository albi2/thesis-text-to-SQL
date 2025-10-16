import json
from typing import List
import re
import asyncio
from typing import Tuple
from components.models.reasoning_model_facade import ReasoningModelFacade
from prompts.schema_filtering import PROMPT as COLUMN_SELECTION_PROMPT, FEWSHOT_EXAMPLES
from prompts.schema_filtering_with_criteria import PROMPT as SCHEMA_FILTERING_WITH_CRITERIA_PROMPT, FEWSHOT_EXAMPLES_WITH_CRITERIA
from context.pipeline_context import PipelineContext
from components.models.api_model_facade import ApiModelFacade
from prompts.preliminary_sql_generation import PRELIMINARY_SQL_PROMPT
from util.db.execute import execute_sql_queries_async, SQLExecInfo
from util.constants import DatabaseConstants
from prompts.sql_extraction import SQL_EXTRACTION_PROMPT
from pipeline.steps.information_retrieval.executor.information_retriever import InformationRetriever

class SchemaFilterExecutor:
    def __init__(self):
        # self.reasoning_model_facade = ReasoningModelFacade()
        self.api_model_default = ApiModelFacade(temperature=0.5)
        self.api_model_gemini_25_lite = ApiModelFacade(model_name="gemini-2.5-flash-lite", temperature=0.3)
        self.information_retriever = InformationRetriever()

    def _prepare_relevant_entities(self, relevant_entities: dict) -> str:
        """
        Formats the relevant entities into a readable string, limiting them to 3 per phrase.
        """
        if not relevant_entities:
            return ""

        entities_by_phrase = {}
        for table, columns in relevant_entities.items():
            for column, entities in columns.items():
                for entity in entities[:3]:
                    phrase = entity["phrase"]
                    if phrase not in entities_by_phrase:
                        entities_by_phrase[phrase] = []
                    entities_by_phrase[phrase].append(f"- {table}.{column} = {entity['value']}")

        output_str = ""
        for phrase, entities in entities_by_phrase.items():
            output_str += f"'{phrase}':\n"
            output_str += "\n".join(entities)
            output_str += "\n\n"
        
        return output_str

    async def _generate_and_execute_preliminary_sql(self, pipeline_context: PipelineContext, mschema_representation: str) -> SQLExecInfo:
        relevant_entities_str = self._prepare_relevant_entities(pipeline_context.relevant_entities)
        
        prompt = PRELIMINARY_SQL_PROMPT.format(
            DATABASE_SCHEMA=mschema_representation,
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            RELEVANT_ENTITIES=relevant_entities_str,
        )

        query_chain = self.api_model_default.get_chain()
        model_response = self.api_model_default.call(query_chain, {"user_prompt": prompt})

        if "```sql" in model_response:
            preliminary_sql = model_response.split("```sql")[1].split("```")[0].strip()
        else:
            preliminary_sql = model_response.strip()

        sql_exec_info = await execute_sql_queries_async([preliminary_sql], DatabaseConstants.DB_PATH, pipeline_context.db_engine)
        
        return sql_exec_info[0]

    async def _extract_sql_components(self, sql_query: str) -> dict:
        prompt = SQL_EXTRACTION_PROMPT.format(SQL_QUERY=sql_query)
        query_chain = self.api_model_default.get_chain()
        model_response = self.api_model_default.call(query_chain, {"user_prompt": prompt})

        try:
            if "```json" in model_response:
                model_response = model_response.split("```json")[1].split("```")[0]
                return json.loads(re.sub(r"^\s+", "", model_response))
        except Exception as e:
            return None

    def execute(self, pipeline_context: PipelineContext) -> List[dict]:
        loop = asyncio.get_event_loop()
        
        # 1. Get unique table and column names from context
        unique_table_names = list(set(col_info["table_name"] for kw_context in pipeline_context.db_schema_per_keyword.values() for col_info in kw_context))
        unique_column_names = list(set(f"{col_info['table_name']}.{col_info['column_name']}" for kw_context in pipeline_context.db_schema_per_keyword.values() for col_info in kw_context))

        if pipeline_context.relevant_entities:
            for table_name, columns in pipeline_context.relevant_entities.items():
                if table_name not in unique_table_names:
                    unique_table_names.append(table_name)
                for column_name in columns.keys():
                    full_column_name = f"{table_name}.{column_name}"
                    if full_column_name not in unique_column_names:
                        unique_column_names.append(full_column_name)

        pipeline_context.unique_table_names = unique_table_names
        pipeline_context.unique_column_names = unique_column_names
        
        # 2. Generate a single schema representation with all retrieved tables and columns
        mschema_representation = pipeline_context.schema_engine.mschema.to_mschema(
            selected_tables=unique_table_names,
            selected_columns=unique_column_names
        )

        if not pipeline_context.relevant_entities:
            # Generate and execute preliminary SQL
            sql_exec_info = asyncio.run(self._generate_and_execute_preliminary_sql(pipeline_context, mschema_representation))
            preliminary_sql = sql_exec_info.sql
            pipeline_context.preliminary_sql = preliminary_sql


            # Extract components from SQL and re-run information retrieval
            sql_components = asyncio.run(self._extract_sql_components(preliminary_sql))
            if sql_components is not None: 
                keywords = sql_components.get("columns", [])
                phrases = sql_components.get("literals", [])

                pipeline_context.relevant_entities = self.information_retriever.retrieve_entities(
                    db_id=pipeline_context.task.db_id,
                    phrases=phrases
                )
                # pipeline_context.db_schema_per_keyword.update(self.information_retriever.retrieve_context(keywords=keywords, task=pipeline_context.task, k = 3))

            # Re-generate unique table and column names
            unique_table_names = list(set(col_info["table_name"] for kw_context in pipeline_context.db_schema_per_keyword.values() for col_info in kw_context))
            unique_column_names = list(set(f"{col_info['table_name']}.{col_info['column_name']}" for kw_context in pipeline_context.db_schema_per_keyword.values() for col_info in kw_context))

            if pipeline_context.relevant_entities:
                for table_name, columns in pipeline_context.relevant_entities.items():
                    if table_name not in unique_table_names:
                        unique_table_names.append(table_name)
                    for column_name in columns.keys():
                        full_column_name = f"{table_name}.{column_name}"
                        if full_column_name not in unique_column_names:
                            unique_column_names.append(full_column_name)

            pipeline_context.unique_table_names = unique_table_names
            pipeline_context.unique_column_names = unique_column_names

        mschema_representation = pipeline_context.schema_engine.mschema.to_mschema(
            selected_tables=unique_table_names,
            selected_columns=unique_column_names
        )
        ddl_schema_representation = pipeline_context.schema_engine.ddl_schema.to_ddl(
            selected_tables=unique_table_names,
            selected_columns=unique_column_names
        )

        # 3. Call LLM to filter the schema
        schemas = loop.run_until_complete(self._filter_schema_concurrently(pipeline_context, mschema_representation, ddl_schema_representation))

        pipeline_context.selected_schemas = schemas
        return pipeline_context.selected_schemas

    async def _filter_schema_concurrently(self, pipeline_context: PipelineContext, mschema_representation: str, ddl_schema_representation: str) -> List[dict]:
        relevant_entities_str = self._prepare_relevant_entities(pipeline_context.relevant_entities)
        
        full_mschema_prompt = COLUMN_SELECTION_PROMPT.format(
            DATABASE_SCHEMA=mschema_representation,
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            RELEVANT_ENTITIES=relevant_entities_str
        )

        full_ddl_schema_prompt = SCHEMA_FILTERING_WITH_CRITERIA_PROMPT.format(
            DATABASE_SCHEMA=ddl_schema_representation,
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            CRITERIA=pipeline_context.query_evaluation_criteria,
            RELEVANT_ENTITIES=relevant_entities_str,
        )

        model_configs = {
            "default": {
                "facade": self.api_model_default,
                "prompt": full_mschema_prompt
            },
            "gemini-2.5-flash-lite": {
                "facade": self.api_model_gemini_25_lite,
                "prompt": full_ddl_schema_prompt
            }
        }

        tasks = [
            self._get_schema_from_model(config["facade"], config["prompt"], model_name)
            for model_name, config in model_configs.items()
        ]
        
        results = await asyncio.gather(*tasks)
        return [schema for schema in results if schema is not None]

    async def _get_schema_from_model(self, facade, prompt, model_name):
        try:
            query_chain = facade.get_chain()
            model_response = await facade.acall(query_chain, {"user_prompt": prompt})
            
            print(f"SCHEMA FILTERING RESPONSE ({model_name}):", model_response)
            
            if "```json" in model_response:
                model_response = model_response.split("```json")[1].split("```")[0]
            
            return json.loads(re.sub(r"^\s+", "", model_response))
        except Exception as e:
            print(f"Could not get or parse response from {model_name}: {e}")
            return None
    
