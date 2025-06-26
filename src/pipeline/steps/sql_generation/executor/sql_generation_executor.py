import json
import re
from typing import List
import asyncio
from components.models.text2sql_model_facade import Text2SQLModelFacade
from context.pipeline_context import PipelineContext
from prompts.sql_generation import PROMPT
from util.db.execute import execute_sql_queries_async, SQLExecInfo

class SQLGenerationExecutor:
    NUM_QUERIES_TO_GENERATE = 3  # Configurable static field

    def __init__(self):
        self.text2sql_model_facade = Text2SQLModelFacade()

    def execute(self, pipeline_context: PipelineContext) -> List[SQLExecInfo]:
        generated_sql_queries: List[str] = []

        # Create MSchema string from selected_schema
        selected_tables = list(pipeline_context.selected_schema.keys())
        selected_columns = []
        for table, columns in pipeline_context.selected_schema.items():
            for col in columns:
                if col != "chain_of_thought_reasoning": # Exclude reasoning from columns
                    selected_columns.append(f"{table}.{col}")

        # Ensure that the schema engine is available in the context
        if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
            raise ValueError("SchemaEngine not found in pipeline context.")

        mschema_string: str = pipeline_context.schema_engine.mschema.to_mschema(
            selected_tables=selected_tables,
            selected_columns=selected_columns,
            show_type_detail=True
        )

        for _ in range(self.NUM_QUERIES_TO_GENERATE):
            full_prompt = PROMPT.format(
                DATABASE_SCHEMA=mschema_string,
                QUESTION=pipeline_context.user_query,
                HINT=getattr(pipeline_context, 'hint', '') # Get hint if it exists, otherwise empty string
            )

            model_response = self.text2sql_model_facade.query(full_prompt)
            
            # Extract SQL from <FINAL_ANSWER> tags
            sql_match = re.search(r"<FINAL_ANSWER>\s*(.*?)\s*</FINAL_ANSWER>", model_response, re.DOTALL)
            if sql_match:
                extracted_sql = sql_match.group(1).strip()
                print(f"Generated SQL: {extracted_sql}")
                generated_sql_queries.append(extracted_sql)
            else:
                print(f"Could not extract SQL from model response: {model_response}")
                # Optionally, append the raw response or skip if no SQL is found
                generated_sql_queries.append(model_response) # Append raw response for now

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
                execute_sql_queries_async(generated_sql_queries, pipeline_context.db_engine)
            )
        else:
            # If no loop is running, create and run a new one.
            executable_sql_infos = loop.run_until_complete(
                execute_sql_queries_async(generated_sql_queries, pipeline_context.db_engine)
            )
        
        pipeline_context.generated_sql_queries = [info for info in executable_sql_infos if info.status == "OK"]
        return [info for info in executable_sql_infos if info.status == "OK"]