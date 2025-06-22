import json
from typing import List, Dict, Any

from components.models.reasoning_model_facade import ReasoningModelFacade
from components.schema.m_schema import MSchema
from prompts.column_selection import PROMPT, FEWSHOT_EXAMPLES


class SchemaFilterExecutor:
    def __init__(self):
        self.reasoning_model_facade = ReasoningModelFacade()

    def execute(self, pipeline_context) -> dict:
        unique_table_names: List[str] = []
        unique_column_names: List[str] = []

        for keyword_contexts in pipeline_context.db_schema_per_keyword.values():
            for column_info in keyword_contexts:
                table_name = column_info.get("table_name")
                column_name = column_info.get("column_name")

                if table_name and table_name not in unique_table_names:
                    unique_table_names.append(table_name)
                if column_name and column_name not in unique_column_names:
                    unique_column_names.append(column_name)

        # The to_mschema method expects selected_tables and selected_columns.
        # We need to pass the unique table names and unique column names.
        # The unique_column_names list contains only column names, not "table.column" format.
        # The to_mschema method will handle the mapping.
        database_schema = pipeline_context.schema_engine.mschema.to_mschema(selected_tables=unique_table_names, selected_columns=unique_column_names)

        full_prompt = PROMPT.format(
            DATABASE_SCHEMA=database_schema,
            QUESTION=pipeline_context.user_query,
            HINT="",
            FEWSHOT_EXAMPLES=FEWSHOT_EXAMPLES,
        )

        model_response = self.reasoning_model_facade.query(full_prompt)
        print(model_response)
        result_dictionary = {}
        try:
            result_dictionary = json.loads(model_response)
        except Exception as e:
            print("Could not parse JSON for schema filtering", e) 

        return result_dictionary