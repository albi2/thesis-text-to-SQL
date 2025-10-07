import json
from typing import List
import re
from components.models.reasoning_model_facade import ReasoningModelFacade
from prompts.schema_filtering import PROMPT as COLUMN_SELECTION_PROMPT, FEWSHOT_EXAMPLES
from prompts.schema_filtering_with_criteria import PROMPT as SCHEMA_FILTERING_WITH_CRITERIA_PROMPT, FEWSHOT_EXAMPLES_WITH_CRITERIA
from context.pipeline_context import PipelineContext
from components.models.api_model_facade import ApiModelFacade

class SchemaFilterExecutor:
    def __init__(self):
        # self.reasoning_model_facade = ReasoningModelFacade()
        self.api_model_default = ApiModelFacade(temperature=0.5)
        self.api_model_gemini_25_lite = ApiModelFacade(model_name="gemini-2.5-flash-lite", temperature=0.5)

    def _prepare_relevant_entities(self, relevant_entities: dict) -> str:
        """
        Formats the relevant entities into a readable string, limiting them to 3 per phrase.
        """
        if not relevant_entities:
            return ""

        entities_by_phrase = {}
        for table, columns in relevant_entities.items():
            for column, entities in columns.items():
                for entity in entities:
                    phrase = entity["phrase"]
                    if phrase not in entities_by_phrase:
                        entities_by_phrase[phrase] = []
                    entities_by_phrase[phrase].append(f"- {table}.{column} = {entity['value']}")

        output_str = ""
        for phrase, entities in entities_by_phrase.items():
            output_str += f"'{phrase}':\n"
            output_str += "\n".join(entities[:3])
            output_str += "\n\n"
        
        return output_str

    def execute(self, pipeline_context: PipelineContext) -> List[dict]:
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
        full_mschema_prompt = COLUMN_SELECTION_PROMPT.format(
            DATABASE_SCHEMA=mschema_representation,
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            FEWSHOT_EXAMPLES=FEWSHOT_EXAMPLES,
        )

        relevant_entities_str = self._prepare_relevant_entities(pipeline_context.relevant_entities)
        full_ddl_schema_prompt = SCHEMA_FILTERING_WITH_CRITERIA_PROMPT.format(
            DATABASE_SCHEMA=ddl_schema_representation,
            QUESTION=pipeline_context.user_query,
            HINT=pipeline_context.task.evidence,
            FEWSHOT_EXAMPLES=FEWSHOT_EXAMPLES_WITH_CRITERIA,
            CRITERIA=pipeline_context.query_evaluation_criteria,
            RELEVANT_ENTITIES=relevant_entities_str,
        )

        # 4. Define model configurations
        model_configs = {
            "default": {
                "facade": self.api_model_default,
                "prompt": full_mschema_prompt
            },
            "gemini-2.5-flash-lite": {
                "facade": self.api_model_gemini_25_lite,
                "prompt": full_ddl_schema_prompt
            }
        }

        # 5. Gather model responses and parse schemas
        schemas = []
        for model_name, config in model_configs.items():
            try:
                facade = config["facade"]
                prompt = config["prompt"]
                
                query_chain = facade.get_chain()
                model_response = facade.invoke_chain(query_chain, {"user_prompt": prompt})
                
                print(f"SCHEMA FILTERING RESPONSE ({model_name}):", model_response)
                
                if "```json" in model_response:
                    model_response = model_response.split("```json")[1].split("```")[0]
                
                resulting_schema = json.loads(re.sub(r"^\s+", "", model_response))
                schemas.append(resulting_schema)
            except Exception as e:
                print(f"Could not get or parse response from {model_name}: {e}")

        pipeline_context.selected_schemas = schemas
        return pipeline_context.selected_schemas
    