import json
import re
from typing import List
import asyncio
from components.models.text2sql_model_facade import Text2SQLModelFacade
from context.pipeline_context import PipelineContext
from prompts.sql_generation import PROMPT, DEFOG_PROMPT, OMNI_PROMPT
from util.db.execute import execute_sql_queries_async, SQLExecInfo, SQLExecStatus
from util.constants import DatabaseConstants, HuggingFaceModelConstants, Text2SQLModelKeys
from pipeline.steps.models.sql_query import SQLQuery
from pipeline.steps.models.schema_representation import SchemaRepresentation, SchemaFormat, SchemaType

class SQLGenerationExecutor:

    def __init__(self):
        self.text2sql_model_facade = Text2SQLModelFacade()
        self.omni_text2sql_model_facade = Text2SQLModelFacade(model_name = HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_PATH, model_repo = HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_REPO)
        self.defog_text2sql_model_facade = Text2SQLModelFacade(model_name = HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_PATH, model_repo = HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_REPO)

    def execute(self, pipeline_context: PipelineContext) -> List[SQLQuery]:
        sql_queries: list[SQLQuery] = []
        if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
            return []

        # 1. Get unique table and column names from the filtered schema
        selected_schema = pipeline_context.selected_schema


        # 2. Generate schema representations
        schema_representations: list[SchemaRepresentation] = []
        ddl_schema_representations: list[SchemaRepresentation] = []

        if len(pipeline_context.schema_engine.get_table_names()) <= 15:
            schema_representations.append(SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(), format=SchemaFormat.M_SCHEMA, type=SchemaType.FULL))
            ddl_schema_representations.append(SchemaRepresentation(schema=pipeline_context.schema_engine.ddl_schema.to_ddl(), format=SchemaFormat.DDL, type=SchemaType.FULL))

<<<<<<< Updated upstream


        if selected_schema:
            selected_tables = [table_name.split('.')[1] if '.' in table_name else table_name for table_name in selected_schema.keys()]
            selected_columns = [f"{table.split('.')[1]}.{col}" if '.' in table else f"{table}.{col}" for table, columns in selected_schema.items() if table != "chain_of_thought_reasoning" for col in columns]
            
            schema_representations.extend([
                SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables, format=SchemaFormat.M_SCHEMA, type=SchemaType.FULL)),
                SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables, selected_columns=selected_columns, format=SchemaFormat.M_SCHEMA, type=SchemaType.FULL))
            ])
            ddl_schema_representations.extend([
                SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables, format=SchemaFormat.DDL, type=SchemaType.FULL)),
                SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables, selected_columns=selected_columns, format=SchemaFormat.DDL, type=SchemaType.FULL))
            ])
        
=======
        schema_representations.extend([
            SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables), format=SchemaFormat.M_SCHEMA, type=SchemaType.FULL),
            SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables, selected_columns=selected_columns), format=SchemaFormat.M_SCHEMA, type=SchemaType.FULL)
        ])
        ddl_schema_representations.extend([
            SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables), format=SchemaFormat.DDL, type=SchemaType.FULL),
            SchemaRepresentation(schema=pipeline_context.schema_engine.mschema.to_mschema(selected_tables=selected_tables, selected_columns=selected_columns), format=SchemaFormat.DDL, type=SchemaType.FULL)
        ])
>>>>>>> Stashed changes

        # 3. Generate SQL queries for each schema representation
        for i, (mschema, ddl_schema) in enumerate(zip(schema_representations, ddl_schema_representations)):
            full_prompt = PROMPT.format(DATABASE_SCHEMA=mschema.schema, QUESTION=pipeline_context.user_query, HINT=getattr(pipeline_context, 'hint', ''))
            defog_prompt = DEFOG_PROMPT.format(DATABASE_SCHEMA=ddl_schema.schema, QUESTION=pipeline_context.user_query, HINT=getattr(pipeline_context, 'hint', ''))
            omni_prompt = OMNI_PROMPT.format(DATABASE_SCHEMA=ddl_schema.schema, QUESTION=pipeline_context.user_query, HINT=getattr(pipeline_context, 'hint', ''))

            model_responses = {
                Text2SQLModelKeys.XIYAN: self.text2sql_model_facade.query(full_prompt),
                Text2SQLModelKeys.DEFOG: self.defog_text2sql_model_facade.query(prompt=defog_prompt, system_prompt=None, max_new_tokens=1024),
                Text2SQLModelKeys.OMNI: self.omni_text2sql_model_facade.query(prompt=omni_prompt, system_prompt=None, max_new_tokens=1024)
            }

            for model_key, model_response in model_responses.items():
                try:
                    print('SQL GENERATION MODEL RESPONSE', model_response)
                    if "```sql" in model_response:
                        query = re.sub(r"^\s+", "", model_response.split("```sql")[1].split("```")[0])
                    elif "```" in model_response:
                        query = model_response.split(";")[0].split("```")[0].strip() + ";"
                    else:
                        query = model_response
                    schema_rep = ddl_schema if model_key in [Text2SQLModelKeys.OMNI, Text2SQLModelKeys.DEFOG] else mschema
                    
                    sql_queries.append(SQLQuery(
                        sql_exec_info=SQLExecInfo(sql=query),
                        schema_representation=schema_rep,
                        model_key=model_key
                    ))
                except Exception as e:
                    print(f"Could not parse response: {e}")

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

        pipeline_context.generated_sql_queries = [query for query in sql_queries if query.sql_exec_info.status == SQLExecStatus.CORRECT_SYNTAX]
        pipeline_context.non_executable_sql_queries = [query for query in sql_queries if query.sql_exec_info.status != SQLExecStatus.CORRECT_SYNTAX]

        return pipeline_context.generated_sql_queries