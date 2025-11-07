import json
from typing import List
import re
import asyncio
from typing import Tuple
from prompts.schema_filtering import PROMPT as COLUMN_SELECTION_PROMPT, FEWSHOT_EXAMPLES
from context.pipeline_context import PipelineContext
from components.models.api_model_facade import ApiModelFacade
from pipeline.steps.information_retrieval.executor.information_retriever import InformationRetriever

class SchemaFilterExecutor:
    def __init__(self):
        # self.reasoning_model_facade = ReasoningModelFacade()
        self.api_model_gemini_25_lite = ApiModelFacade(model_name="gemini-2.5-flash-lite", temperature=0.2)
        self.information_retriever = InformationRetriever()

    async def _get_initial_schema(self, pipeline_context: PipelineContext, ignored_columns: List[str] = None) -> dict:
        """
        Queries the LLM for the initial schema.
        """
        # relevant_entities_str = self._prepare_relevant_entities(pipeline_context.relevant_entities)

        prompt = COLUMN_SELECTION_PROMPT.format(
            DATABASE_SCHEMA=pipeline_context.schema_engine.mschema.to_mschema(
                selected_tables=pipeline_context.unique_table_names,
                selected_columns=pipeline_context.unique_column_names,
                ignored_columns=ignored_columns
            ),
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            FEWSHOT_EXAMPLES=FEWSHOT_EXAMPLES
        )

        query_chain = self.api_model_gemini_25_lite.get_chain()
        model_response = await self.api_model_gemini_25_lite.acall(query_chain, {"user_prompt": prompt})

        try:
            if "```json" in model_response:
                model_response = model_response.split("```json")[1].split("```")[0]
            initial_schema = json.loads(re.sub(r"^\s+", "", model_response))
            return initial_schema
        except Exception as e:
            print(f"Could not get or parse response from LLM: {e}")
            return None

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

    def execute(self, pipeline_context: PipelineContext) -> List[dict]:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

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

        # 2. Get initial schema from LLM
        initial_schema_1 = loop.run_until_complete(self._get_initial_schema(pipeline_context))

        # 3. Extract columns and tables from the initial schema
        table_names_1, column_names_1 = self._extract_tables_and_columns(initial_schema_1)

        # 4. Create a list of columns that are not PKs or FKs
        ignored_columns_1 = []
        for table_name in table_names_1:
            for column_name in initial_schema_1[table_name]:
                if not pipeline_context.schema_engine.is_primary_key(table_name, column_name) and not pipeline_context.schema_engine.is_foreign_key(table_name, column_name):
                    ignored_columns_1.append(f"{table_name}.{column_name}")

        # 5. Call LLM again with the list of ignored columns
        initial_schema_2 = loop.run_until_complete(self._get_initial_schema(pipeline_context, ignored_columns_1))

        # 6. Extract columns and tables from the second initial schema
        table_names_2, column_names_2 = self._extract_tables_and_columns(initial_schema_2)

        # 7. Create a list of columns that are not PKs or FKs in the second schema
        ignored_columns_2 = []
        for table_name in table_names_2:
            for column_name in initial_schema_2[table_name]:
                if not pipeline_context.schema_engine.is_primary_key(table_name, column_name) and not pipeline_context.schema_engine.is_foreign_key(table_name, column_name):
                    ignored_columns_2.append(f"{table_name}.{column_name}")

        # 8. Call LLM again ignoring the columns from both initial schemas
        initial_schema_3 = loop.run_until_complete(self._get_initial_schema(pipeline_context, ignored_columns_1 + ignored_columns_2))

        # 9. Create the final schemas
        schema_1 = initial_schema_1
        schema_2 = self._merge_schemas(initial_schema_1, initial_schema_2)
        schema_3 = self._merge_schemas(initial_schema_2, initial_schema_3)

        pipeline_context.selected_schemas = [schema_1, schema_2, schema_3]
        return pipeline_context.selected_schemas

    def _merge_schemas(self, schema1: dict, schema2: dict) -> dict:
        """
        Merges two schemas into a single schema.
        """
        merged_schema = schema1.copy()
        for table, columns in schema2.items():
            if table in merged_schema:
                merged_schema[table] = list(set(merged_schema[table] + columns))
            else:
                merged_schema[table] = columns
        return merged_schema

   
    def _extract_tables_and_columns(self, initial_schema: dict) -> Tuple[List[str], List[str]]:
        """
        Extracts table and column names from the initial schema.
        """
        table_names = []
        column_names = []
        for table, columns in initial_schema.items():
            if table == "chain_of_thought_reasoning":
                continue
            table_names.append(table)
            for column in columns:
                column_names.append(f"{table}.{column}")
        return table_names, column_names

    
