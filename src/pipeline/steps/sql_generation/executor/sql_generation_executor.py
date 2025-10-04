import json
import re
from typing import List, Tuple
import asyncio
from components.models.text2sql_model_facade import Text2SQLModelFacade
from context.pipeline_context import PipelineContext
from prompts.sql_generation import PROMPT, DEFOG_PROMPT, OMNI_PROMPT, ORIGINAL_PROMPT
from util.db.execute import execute_sql_queries_async, SQLExecInfo, SQLExecStatus
from util.constants import DatabaseConstants, HuggingFaceModelConstants, Text2SQLModelKeys
from pipeline.steps.models.sql_query import SQLQuery
from pipeline.steps.models.schema_representation import SchemaRepresentation, SchemaFormat, SchemaType
from components.models.api_model_facade import ApiModelFacade

class SQLGenerationExecutor:

    def __init__(self):
        self.text2sql_model_facade = Text2SQLModelFacade()
        self.omni_text2sql_model_facade = Text2SQLModelFacade(model_name = HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_PATH, model_repo = HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_REPO)
        self.defog_text2sql_model_facade = Text2SQLModelFacade(model_name = HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_PATH, model_repo = HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_REPO)
        self.api_model_gemini = ApiModelFacade(model_name="gemini-2.5-flash", temperature=0.2)

    def execute(self, pipeline_context: PipelineContext) -> List[SQLQuery]:
        if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
            return []

        schema_representations, ddl_schema_representations = self._generate_schema_representations(pipeline_context)
        
        sql_queries = self._generate_sql_for_gemini(pipeline_context, schema_representations)
        # sql_queries.extend(self._generate_sql_for_small_models(pipeline_context, schema_representations, ddl_schema_representations))
        
        self._execute_queries_async(pipeline_context, sql_queries)

        pipeline_context.generated_sql_queries = [query for query in sql_queries if query.sql_exec_info.status == SQLExecStatus.CORRECT_SYNTAX]
        pipeline_context.non_executable_sql_queries = [query for query in sql_queries if query.sql_exec_info.status != SQLExecStatus.CORRECT_SYNTAX]

        return pipeline_context.generated_sql_queries

    def _generate_schema_representations(self, pipeline_context: PipelineContext) -> Tuple[List[SchemaRepresentation], List[SchemaRepresentation]]:
        schema_representations: list[SchemaRepresentation] = []
        ddl_schema_representations: list[SchemaRepresentation] = []
        selected_schemas = pipeline_context.selected_schemas

        if len(pipeline_context.schema_engine.get_table_names()) <= 7:
            schema_representations.append(SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(), format=SchemaFormat.M_SCHEMA, type=SchemaType.FULL))
            ddl_schema_representations.append(SchemaRepresentation(schema=pipeline_context.schema_engine.ddl_schema.to_ddl(), format=SchemaFormat.DDL, type=SchemaType.FULL))

        if selected_schemas:
            for selected_schema in selected_schemas:
                reasoning = selected_schema.get('chain_of_thought_reasoning')
                execution_plan = f"Execution plan: {reasoning}" if reasoning else ""
                
                selected_tables = [table_name.split('.')[1] if '.' in table_name else table_name for table_name in selected_schema.keys()]
                selected_columns = [f"{table.split('.')[1]}.{col}" if '.' in table else f"{table}.{col}" for table, columns in selected_schema.items() if table != "chain_of_thought_reasoning" for col in columns]

                schema_representations.append(SchemaRepresentation(
                    schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables),
                    format=SchemaFormat.M_SCHEMA,
                    type=SchemaType.FILTERED_TABLES,
                    execution_plan=execution_plan
                ))
                ddl_schema_representations.append(SchemaRepresentation(
                    schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables),
                    format=SchemaFormat.DDL,
                    type=SchemaType.FILTERED_TABLES,
                    execution_plan=execution_plan
                ))

                schema_representations.append(SchemaRepresentation(
                    schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables, selected_columns=selected_columns),
                    format=SchemaFormat.M_SCHEMA,
                    type=SchemaType.FILTERED_TABLES_AND_COLUMNS,
                    execution_plan=execution_plan
                ))
                ddl_schema_representations.append(SchemaRepresentation(
                    schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables, selected_columns=selected_columns),
                    format=SchemaFormat.DDL,
                    type=SchemaType.FILTERED_TABLES_AND_COLUMNS,
                    execution_plan=execution_plan
                ))

        return schema_representations, ddl_schema_representations

    def _generate_sql_for_gemini(self, pipeline_context: PipelineContext, schema_representations: List[SchemaRepresentation]) -> List[SQLQuery]:
        sql_queries: list[SQLQuery] = []
        for mschema in schema_representations:
            try:
                hint = getattr(pipeline_context, 'hint', '')
                execution_plan = getattr(mschema, 'execution_plan', '')
                if execution_plan:
                    hint = f"{hint}\n{execution_plan}"
                
                full_prompt = ORIGINAL_PROMPT.format(DATABASE_SCHEMA=mschema.schema, QUESTION=pipeline_context.user_query, HINT=hint)
                query_chain = self.api_model_gemini.get_chain()
                model_response = self.api_model_gemini.invoke_chain(query_chain, {"user_prompt": full_prompt})

                print('SQL GENERATION MODEL RESPONSE (GEMINI)', model_response)
                if "```sql" in model_response:
                    query = re.sub(r"^\s+", "", model_response.split("```sql")[1].split("```")[0])
                elif "```" in model_response:
                    query = model_response.split(";")[0].split("```")[0].strip() + ";"
                else:
                    query = model_response
                
                sql_queries.append(SQLQuery(
                    sql_exec_info=SQLExecInfo(sql=query),
                    schema_representation=mschema,
                    model_key=Text2SQLModelKeys.GEMINI
                ))
            except Exception as e:
                print(f"Could not parse response from Gemini: {e}")
        return sql_queries

    def _generate_sql_for_small_models(self, pipeline_context: PipelineContext, schema_representations: List[SchemaRepresentation], ddl_schema_representations: List[SchemaRepresentation]) -> List[SQLQuery]:
        sql_queries: list[SQLQuery] = []
        
        model_prompts = {
            Text2SQLModelKeys.XIYAN: [],
            Text2SQLModelKeys.DEFOG: [],
            Text2SQLModelKeys.OMNI: []
        }

        shortened_schema_rep = schema_representations[:3]
        shortened_ddl_schema_representations = ddl_schema_representations[:3]

        for mschema, ddl_schema in zip(shortened_schema_rep, shortened_ddl_schema_representations):
            if mschema.type not in [SchemaType.FILTERED_TABLES_AND_COLUMNS]:
                continue

            hint = getattr(pipeline_context, 'hint', '')
            execution_plan = getattr(mschema, 'execution_plan', '')
            if execution_plan:
                hint = f"{hint}\n{execution_plan}"

            model_prompts[Text2SQLModelKeys.XIYAN].append({
                "prompt": PROMPT.format(DATABASE_SCHEMA=mschema.schema, QUESTION=pipeline_context.user_query, HINT=hint),
                "schema_rep": mschema
            })
            model_prompts[Text2SQLModelKeys.DEFOG].append({
                "prompt": DEFOG_PROMPT.format(DATABASE_SCHEMA=ddl_schema.schema, QUESTION=pipeline_context.user_query, HINT=hint),
                "schema_rep": ddl_schema
            })
            model_prompts[Text2SQLModelKeys.OMNI].append({
                "prompt": OMNI_PROMPT.format(DATABASE_SCHEMA=ddl_schema.schema, QUESTION=pipeline_context.user_query, HINT=hint),
                "schema_rep": ddl_schema
            })

        model_facades = {
            Text2SQLModelKeys.XIYAN: self.text2sql_model_facade,
            Text2SQLModelKeys.DEFOG: self.defog_text2sql_model_facade,
            Text2SQLModelKeys.OMNI: self.omni_text2sql_model_facade
        }

        for model_key, prompts_with_schemas in model_prompts.items():
            if not prompts_with_schemas:
                continue

            model_facade = model_facades[model_key]
            try:
                model_facade.load_model_and_tokenizer()

                for item in prompts_with_schemas:
                    prompt = item["prompt"]
                    schema_rep = item["schema_rep"]
                    
                    try:
                        model_response = model_facade.query(prompt)
                        print(f'SQL GENERATION MODEL RESPONSE ({model_key})', model_response)
                        
                        if "```sql" in model_response:
                            query = re.sub(r"^\s+", "", model_response.split("```sql")[1].split("```")[0])
                        elif "```" in model_response:
                            query = model_response.split(";")[0].split("```")[0].strip() + ";"
                        else:
                            query = model_response
                        
                        sql_queries.append(SQLQuery(
                            sql_exec_info=SQLExecInfo(sql=query),
                            schema_representation=schema_rep,
                            model_key=model_key
                        ))
                    except Exception as e:
                        print(f"Could not parse response from {model_key}: {e}")
            
            except Exception as e:
                print(f"Failed to process model {model_key}: {e}")
            finally:
                model_facade.unload_model()

        return sql_queries

    def _execute_queries_async(self, pipeline_context: PipelineContext, sql_queries: List[SQLQuery]):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        raw_queries = [sql_query.sql_exec_info.sql for sql_query in sql_queries]
        
        executable_sql_infos = loop.run_until_complete(
            execute_sql_queries_async(raw_queries, DatabaseConstants.DB_PATH, pipeline_context.db_engine)
        )

        for sql_query, sql_exec_info in zip(sql_queries, executable_sql_infos):
            sql_query.sql_exec_info = sql_exec_info