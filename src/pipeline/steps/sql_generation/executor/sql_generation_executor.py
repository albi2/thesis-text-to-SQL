import json
import re
from typing import List
import asyncio
from components.models.text2sql_model_facade import Text2SQLModelFacade
from context.pipeline_context import PipelineContext
from prompts.sql_generation import PROMPT, DEFOG_PROMPT
from util.db.execute import execute_sql_queries_async, SQLExecInfo, SQLExecStatus
from util.constants import DatabaseConstants, HuggingFaceModelConstants

class SQLGenerationExecutor:

    def __init__(self):
        self.text2sql_model_facade = Text2SQLModelFacade()
        # self.omin_text2sql_model_facade = Text2SQLModelFacade(model_name = HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_PATH, model_repo = HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_REPO)
        self.defog_text2sql_model_facade = Text2SQLModelFacade(model_name = HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_PATH, model_repo = HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_REPO)

    def execute(self, pipeline_context: PipelineContext) -> List[SQLExecInfo]:
        all_generated_queries = []
        for selected_schema in pipeline_context.selected_schemas:
            selected_tables = [table_name.split('.')[1] for table_name in selected_schema.keys() if '.' in table_name]
            selected_columns = [f"{table.split('.')[1]}.{col}" if '.' in table else f"{table}.{col}" for table, columns in selected_schema.items() if table != "chain_of_thought_reasoning" for col in columns]

            if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
                continue

            mschema_string = pipeline_context.schema_engine.mschema.to_mschema(
                selected_tables=selected_tables,
                selected_columns=selected_columns,
                show_type_detail=True
            )

            print('SQL GENERATION MSCHEMA', mschema_string)

            full_prompt = PROMPT.format(DATABASE_SCHEMA=mschema_string, QUESTION=pipeline_context.user_query, HINT=getattr(pipeline_context, 'hint', ''))
            defog_prompt = DEFOG_PROMPT.format(DATABASE_SCHEMA=mschema_string, QUESTION=pipeline_context.user_query)

            responses = []
            try:
                responses.append(self.text2sql_model_facade.query(full_prompt))
                responses.append(self.defog_text2sql_model_facade.query(prompt=defog_prompt, system_prompt=None, max_new_tokens=800))
            except Exception as e:
                print(f"Failed to generate query because of {e}")

            for model_response in responses:
                try:
                    print('SQL GENERATION MODEL RESPONSE', model_response)
                    if "```sql" in model_response:
                        all_generated_queries.append(re.sub(r"^\s+", "", model_response.split("```sql")[1].split("```")[0]))
                    elif "```" in model_response:
                        all_generated_queries.append(model_response.split(";")[0].split("```")[0].strip() + ";")
                    else:
                        all_generated_queries.append(model_response)
                except Exception as e:
                    print(f"Could not parse response: {e}")
                    all_generated_queries.append(model_response)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        executable_sql_infos = loop.run_until_complete(
            execute_sql_queries_async(all_generated_queries, DatabaseConstants.DB_PATH, pipeline_context.db_engine)
        )

        pipeline_context.generated_sql_queries = [info for info in executable_sql_infos if info.status == SQLExecStatus.CORRECT_SYNTAX]
        pipeline_context.non_executable_sql_queries = [info for info in executable_sql_infos if info.status != SQLExecStatus.CORRECT_SYNTAX]

        return pipeline_context.generated_sql_queries