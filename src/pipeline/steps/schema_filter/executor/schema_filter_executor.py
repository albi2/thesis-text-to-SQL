import json
from typing import List
import re
from components.models.reasoning_model_facade import ReasoningModelFacade
from components.schema.m_schema import MSchema
from prompts.column_selection import PROMPT, FEWSHOT_EXAMPLES
from context.pipeline_context import PipelineContext

class SchemaFilterExecutor:
    def __init__(self):
        self.reasoning_model_facade = ReasoningModelFacade()

    def execute(self, pipeline_context: PipelineContext) -> dict:
        unique_table_names: List[str] = []
        unique_column_names: List[str] = []

        for keyword_contexts in pipeline_context.db_schema_per_keyword.values():
            for column_info in keyword_contexts:
                table_name = column_info.get("table_name")
                column_name = column_info.get("column_name")

                if table_name and table_name not in unique_table_names:
                    unique_table_names.append(table_name)
                if column_name and column_name not in unique_column_names:
                    unique_column_names.append(table_name + "." + column_name)

        # The to_mschema method expects selected_tables and selected_columns.
        # We need to pass the unique table names and unique column names.
        # The unique_column_names list contains only column names, not "table.column" format.
        # The to_mschema method will handle the mapping. 
        database_schema = pipeline_context.schema_engine.mschema.to_mschema(selected_tables=unique_table_names, selected_columns=unique_column_names)
        print(f"SCHEMA USED FOR FILTERING", database_schema)

        ## TODO: These table names are included in the prompt in format(database.table) -> this adds extra effort for model which we might want to avoid
        full_prompt = PROMPT.format(
            DATABASE_SCHEMA=database_schema,
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            FEWSHOT_EXAMPLES=FEWSHOT_EXAMPLES,
        )

        model_response = self.reasoning_model_facade.query(full_prompt)
        
        print('FILTERING RESPONSE', model_response)
        resulting_schema = {}
        try:
            if "```json" in model_response:
                model_response = model_response.split("```json")[1].split("```")[0]
                model_response = re.sub(r"^\s+", "", model_response)
                resulting_schema = json.loads(model_response)
            else:
                resulting_schema = json.loads(model_response)
        except Exception as e:
            print("Could not parse JSON during schema filtering", e) 

        pipeline_context.selected_schema = resulting_schema
        

        # TODO: See if more porcessing is need here for a better format of representation of chosen tables and columns - maybe some extra filtering or retry in case
        # something does not exist in the database at all
        # TODO: Add the schema to the tables that are missing it in the name so we need schema.table
        return resulting_schema
    