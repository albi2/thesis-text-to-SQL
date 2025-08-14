import re
from typing import List
from components.models.reasoning_model_facade import ReasoningModelFacade
from context.pipeline_context import PipelineContext
from prompts.query_selection import PROMPT
from util.db.execute import SQLExecInfo


class QuerySelectionExecutor:
    def __init__(self):
        self.reasoning_model_facade = ReasoningModelFacade()

    def execute(self, pipeline_context: PipelineContext) -> SQLExecInfo:
        queries_with_results = ""
        for i, info in enumerate(pipeline_context.generated_sql_queries):
            queries_with_results += f"{i}: {info.sql}\n"
            if info.result is not None:
                queries_with_results += f"  Query output: {info.result[:500]}\n"

        if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
            raise ValueError("SchemaEngine not found in pipeline context.")

        selected_tables = [table_name.split('.')[1] for table_name in pipeline_context.selected_schema.keys() if '.' in table_name]
        selected_columns = []
        for table, columns in pipeline_context.selected_schema.items():
            for col in columns:
                if table != "chain_of_thought_reasoning":
                    selected_columns.append(f"{table.split('.')[1]}.{col}")
        
        mschema_string: str = pipeline_context.schema_engine.mschema.to_mschema(
            selected_tables=selected_tables,
            selected_columns=selected_columns,
            show_type_detail=True
        )

        full_prompt = PROMPT.format(
            DATABASE_SCHEMA=mschema_string,
            QUESTION=pipeline_context.user_query,
            HINT=getattr(pipeline_context, 'hint', ''),
            QUERIES=queries_with_results
        )

        model_response = self.reasoning_model_facade.query(full_prompt)

        try:
            match = re.search(r"query_index:\s*(\d+)", model_response)
            if match:
                query_index = int(match.group(1))
                return pipeline_context.generated_sql_queries[query_index]
        except (ValueError, IndexError) as e:
            print(f"Could not parse query index from model response: {e}")
            # Fallback to selecting the first query if parsing fails
            return pipeline_context.generated_sql_queries[0]
        
        # Fallback if no match is found
        return pipeline_context.generated_sql_queries[0]