import json
from typing import List
import re
from components.models.reasoning_model_facade import ReasoningModelFacade
from prompts.column_selection import PROMPT, FEWSHOT_EXAMPLES
from context.pipeline_context import PipelineContext
from components.models.api_model_facade import ApiModelFacade

class SchemaFilterExecutor:
    def __init__(self):
        # self.reasoning_model_facade = ReasoningModelFacade()
        self.api_model_default = ApiModelFacade()
        self.api_model_gemini_25_lite = ApiModelFacade(model_name="gemini-2.5-flash-lite")

    def execute(self, pipeline_context: PipelineContext) -> List[dict]:
        # 1. Get unique table and column names from context
        unique_table_names = list(set(col_info["table_name"] for kw_context in pipeline_context.db_schema_per_keyword.values() for col_info in kw_context))
        unique_column_names = list(set(f"{col_info['table_name']}.{col_info['column_name']}" for kw_context in pipeline_context.db_schema_per_keyword.values() for col_info in kw_context))

        if pipeline_context.entities_db_descriptor and pipeline_context.entities_db_descriptor.tables:
            for table_name, table in pipeline_context.entities_db_descriptor.tables.items():
                if table_name not in unique_table_names:
                    unique_table_names.append(table_name)
                for column_name in table.columns:
                    full_column_name = f"{table_name}.{column_name}"
                    if full_column_name not in unique_column_names:
                        unique_column_names.append(full_column_name)

        # 2. Generate a single schema representation with all retrieved tables and columns
        mschema_representation = pipeline_context.schema_engine.mschema.to_mschema(
            selected_tables=unique_table_names,
            selected_columns=unique_column_names
        )

        ddl_schema_representation = pipeline_context.schema_engine.ddl_schema.to_ddl(
            selected_tables=unique_table_names,
            selected_columns=unique_column_names
        )

        # 3. Call LLM to filter the schema
        full_mschema_prompt = PROMPT.format(
            DATABASE_SCHEMA=mschema_representation,
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            FEWSHOT_EXAMPLES=FEWSHOT_EXAMPLES,
        )

        full_ddl_schema_prompt = PROMPT.format(
            DATABASE_SCHEMA=ddl_schema_representation,
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            FEWSHOT_EXAMPLES=FEWSHOT_EXAMPLES,
        )

        # 4. Gather model responses
        model_responses = []

        query_chain = self.api_model_default.get_chain()
        mschema_model_response = self.api_model_default.invoke_chain(query_chain, {"user_prompt": full_mschema_prompt})
        model_responses.append(mschema_model_response)

        ddl_query_chain = self.api_model_gemini_25_lite.get_chain()
        ddl_model_response = self.api_model_gemini_25_lite.invoke_chain(ddl_query_chain, {"user_prompt": full_ddl_schema_prompt})
        model_responses.append(ddl_model_response)


        # 4. Gather model responses
        schemas = []
        try:
            for model_response in model_responses:
                print(f"SCHEMA FILTERING RESPONSE:", model_response)
                if "```json" in model_response:
                    model_response = model_response.split("```json")[1].split("```")[0]
                resulting_schema = json.loads(re.sub(r"^\s+", "", model_response))
                schemas.append(resulting_schema)
        except Exception as e:
            print(f"Could not parse JSON during schema filtering: {e}")
            pipeline_context.selected_schemas = []

        pipeline_context.selected_schemas = schemas
        return pipeline_context.selected_schemas
    