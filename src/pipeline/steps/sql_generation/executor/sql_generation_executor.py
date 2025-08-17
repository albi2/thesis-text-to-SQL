import json
import re
from typing import List
import asyncio
from components.models.text2sql_model_facade import Text2SQLModelFacade
from context.pipeline_context import PipelineContext
from prompts.sql_generation import PROMPT, DEFOG_PROMPT
from util.db.execute import execute_sql_queries_async, SQLExecInfo
from util.constants import HuggingFaceModelConstants
import time

class SQLGenerationExecutor:

    def __init__(self):
        self.text2sql_model_facade = Text2SQLModelFacade()
        # self.omin_text2sql_model_facade = Text2SQLModelFacade(model_name = HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_PATH, model_repo = HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_REPO)
        self.defog_text2sql_model_facade = Text2SQLModelFacade(model_name = HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_PATH, model_repo = HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_REPO)

    def execute(self, pipeline_context: PipelineContext) -> List[SQLExecInfo]:
        # Create MSchema string from selected_schema
        selected_tables = [table_name.split('.')[1] for table_name in pipeline_context.selected_schema.keys() if '.' in table_name ]
        selected_columns = []
        for table, columns in pipeline_context.selected_schema.items():
            for col in columns:
                if table != "chain_of_thought_reasoning": # Exclude reasoning from columns
                    selected_columns.append(f"{table.split('.')[1]}.{col}")

        # Ensure that the schema engine is available in the context
        if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
            raise ValueError("SchemaEngine not found in pipeline context.")

        mschema_string: str = pipeline_context.schema_engine.mschema.to_mschema(
            selected_tables=selected_tables,
            selected_columns=selected_columns,
            show_type_detail=True
        )

        print('SQL GENERATION MSCHEMA', mschema_string)

        full_prompt = PROMPT.format(
            DATABASE_SCHEMA=mschema_string,
            QUESTION=pipeline_context.user_query,
            HINT=getattr(pipeline_context, 'hint', '') # Get hint if it exists, otherwise empty string
        )

        defog_prompt = DEFOG_PROMPT.format(
            DATABASE_SCHEMA=mschema_string,
            QUESTION=pipeline_context.user_query,
        )

        responses: List[str] = []
        try:
            default_response = self.text2sql_model_facade.query(full_prompt)
            print('FIRST RESPONSE', default_response)
            responses.append(default_response)
            defog_response = self.defog_text2sql_model_facade.query(prompt = defog_prompt, system_prompt = None, max_new_tokens = 800)
            responses.append(defog_response)
            print('SECOND RESPONSE', defog_response)
        except Exception as e:
            print("Failed to generate query because of", e)

        generated_sql_queries: List[str] = []
        for model_response in responses:
            try:
                print('SQL GENERATION MODEL RESPONSE', model_response)
                if "```sql" in model_response:
                    model_response = model_response.split("```sql")[1].split("```")[0]
                    model_response = re.sub(r"^\s+", "", model_response)
                    resulting_sql = json.loads(model_response)
                    generated_sql_queries.append(resulting_sql) # Append raw response for now
                elif "```" in model_response:
                    resulting_sql = generated_text.split(";")[0].split("```")[0].strip()+ ";";
                    generated_sql_queries.append(resulting_sql)
            except Exception as e:
                print("Could not parse JSON for schema filtering", e) 
                generated_sql_queries.append(model_response) 
        

        # Execute and filter queries asynchronously
        # We need to run the async function in an event loop.
        # Since 'execute' is a synchronous method, we create a new event loop for it.
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If a loop is already running (e.g., in a Jupyter notebook or another async context),
            # we need to run the task in the existing loop.
            # This is a simplified approach; for complex scenarios, consider a dedicated task runner.
            executable_sql_infos = loop.run_until_complete(
                execute_sql_queries_async(generated_sql_queries, pipeline_context.db_engine, "thesis") # Store the schema/s and other relevant info in the context
            )
        else:
            # If no loop is running, create and run a new one.
            executable_sql_infos = loop.run_until_complete(
                execute_sql_queries_async(generated_sql_queries, pipeline_context.db_engine, "thesis")
            )

        for executable in executable_sql_infos:
            print('QUERY EXECUTION', executable.to_dict())
        
        pipeline_context.generated_sql_queries = [info for info in executable_sql_infos if info.status == "OK"]
        return [info for info in executable_sql_infos if info.status == "OK"]