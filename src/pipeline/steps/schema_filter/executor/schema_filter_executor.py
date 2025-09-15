import json
from typing import List
import re
from components.models.reasoning_model_facade import ReasoningModelFacade
from components.schema.m_schema import MSchemaGenerator
from prompts.column_selection import PROMPT, FEWSHOT_EXAMPLES
from context.pipeline_context import PipelineContext

class SchemaFilterExecutor:
    def __init__(self):
        self.reasoning_model_facade = ReasoningModelFacade()

    def execute(self, pipeline_context: PipelineContext) -> List[dict]:
        # 1. Get unique table and column names from context
        unique_table_names = list(set(col_info["table_name"] for kw_context in pipeline_context.db_schema_per_keyword.values() for col_info in kw_context))
        unique_column_names = list(set(f"{col_info['table_name']}.{col_info['column_name']}" for kw_context in pipeline_context.db_schema_per_keyword.values() for col_info in kw_context))

        if pipeline_context.entities_db_descriptor:
            for table_name, table in pipeline_context.entities_db_descriptor.tables.items():
                if table_name not in unique_table_names:
                    unique_table_names.append(table_name)
                for column_name in table.columns:
                    full_column_name = f"{table_name}.{column_name}"
                    if full_column_name not in unique_column_names:
                        unique_column_names.append(full_column_name)

        # 2. Generate three schema representations
        schema_representations = [
            pipeline_context.schema_engine.mschema.to_mschema(),
            pipeline_context.schema_engine.mschema.to_mschema(selected_tables=unique_table_names),
            pipeline_context.schema_engine.mschema.to_mschema(selected_tables=unique_table_names, selected_columns=unique_column_names)
        ]

        # 3. Call LLM for each representation and store results
        for i, db_schema in enumerate(schema_representations):
            print(f"SCHEMA USED FOR FILTERING (Representation {i+1}):", db_schema)
            full_prompt = PROMPT.format(
                DATABASE_SCHEMA=db_schema,
                QUESTION=pipeline_context.user_query,
                HINT=pipeline_context.task.evidence,
                FEWSHOT_EXAMPLES=FEWSHOT_EXAMPLES,
            )

            model_response = self.reasoning_model_facade.query(full_prompt)
            print(f"FILTERING RESPONSE (Representation {i+1}):", model_response)

            try:
                if "```json" in model_response:
                    model_response = model_response.split("```json")[1].split("```")[0]
                resulting_schema = json.loads(re.sub(r"^\s+", "", model_response))
                pipeline_context.selected_schemas.append(resulting_schema)
            except Exception as e:
                print(f"Could not parse JSON during schema filtering for representation {i+1}: {e}")

        # For backward compatibility, set selected_schema to the last one
        if pipeline_context.selected_schemas:
            pipeline_context.selected_schema = pipeline_context.selected_schemas[-1]

        return pipeline_context.selected_schemas
    