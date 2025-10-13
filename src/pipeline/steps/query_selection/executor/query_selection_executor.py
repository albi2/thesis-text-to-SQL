import re
import json
from typing import List
from components.models.reasoning_model_facade import ReasoningModelFacade
from context.pipeline_context import PipelineContext
from prompts.query_selection import PROMPT as QUERY_SELECTION_PROMPT
from prompts.criteria_generation import PROMPT as CRITERIA_GENERATION_PROMPT
from util.db.execute import SQLExecInfo, compare_sqls_outcomes
from util.constants import DatabaseConstants, Text2SQLModelKeys
from components.models.api_model_facade import ApiModelFacade

class QuerySelectionExecutor:
    MAJORITY_THRESHOLD = 0.5
    MAX_RETRIES = 2
    MAX_QUERIES_PER_GROUP = 3

    def __init__(self):
        self.api_model = ApiModelFacade()

    def _prepare_relevant_entities(self, relevant_entities: dict) -> str:
        if not relevant_entities:
            return ""
        entities_by_phrase = {
            entity["phrase"]: entities_by_phrase.get(entity["phrase"], []) + [f"- {table}.{column} = {entity['value']}"]
            for table, columns in relevant_entities.items()
            for column, entities in columns.items()
            for entity in entities
        }
        return "\n\n".join([f"'{phrase}':\n" + "\n".join(entities) for phrase, entities in entities_by_phrase.items()]) + "\n\n"

    def execute(self, pipeline_context: PipelineContext) -> SQLExecInfo:
        clusters = self._cluster_equivalent_queries(pipeline_context)

        if len(clusters) == 1:
            return clusters[0][0]

        selected_queries = [
            query for cluster in clusters for query in sorted(
                cluster, key=lambda q: Text2SQLModelKeys.TEXT2SQL_MODEL_CONFIGS.get(q.model_key, {}).get("priority", 99)
            )[:self.MAX_QUERIES_PER_GROUP]
        ]

        queries_with_results = ""
        query_index = 0
        for i, cluster in enumerate(clusters):
            queries_with_results += f"--- Query Group {i+1} (Votes: {len(cluster)}) ---\n"
            sorted_cluster = sorted(cluster, key=lambda q: Text2SQLModelKeys.TEXT2SQL_MODEL_CONFIGS.get(q.model_key, {}).get("priority", 99))
            
            for info in sorted_cluster[:self.MAX_QUERIES_PER_GROUP]:
                queries_with_results += f"{query_index}: {info.sql_exec_info.sql}\n"
                queries_with_results += f"  Execution Status: {info.sql_exec_info.status.value}\n"
                if info.sql_exec_info.result is not None:
                    queries_with_results += f"  Query Output: {str(info.sql_exec_info.result)}\n"
                query_index += 1

        if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
            raise ValueError("SchemaEngine not found in pipeline context.")

        mschema_string = pipeline_context.schema_engine.mschema.to_mschema(show_type_detail=True)
        filtered_schemas_str = self._prepare_filtered_schemas(pipeline_context.selected_schemas)
        
        full_prompt = QUERY_SELECTION_PROMPT.format(
            DATABASE_SCHEMA=mschema_string,
            FILTERED_SCHEMAS=filtered_schemas_str,
            QUESTION=pipeline_context.user_query,
            HINT=getattr(pipeline_context, 'hint', ''),
            CRITERIA=pipeline_context.query_evaluation_criteria,
            QUERIES=queries_with_results
        )
        
        for attempt in range(self.MAX_RETRIES):
            model_response = self.api_model.invoke_chain(self.api_model.get_chain(), {"user_prompt": full_prompt})
            try:
                match = re.search(r"reasoning:\s*(.*?)\s*query_index:\s*(\d+)", model_response, re.DOTALL)
                if match:
                    reasoning, query_index_str = match.groups()
                    query_index = int(query_index_str)
                    pipeline_context.query_selection_reasoning = reasoning.strip()
                    return selected_queries[query_index]
            except (ValueError, IndexError) as e:
                print(f"Attempt {attempt + 1} failed: Could not parse query index or reasoning from model response: {e}")
                pipeline_context.query_selection_reasoning = model_response
        
        print("All retries failed. Returning the first query.")
        return selected_queries[0] if selected_queries else None

    def _prepare_filtered_schemas(self, filtered_schemas: List[dict]) -> str:
        """
        Formats the filtered schemas into a readable string and removes the 'chain_of_thought_reasoning' field.
        """
        if not filtered_schemas:
            return ""

        output_str = ""
        for schema in filtered_schemas:
            for table, columns in schema.items():
                if table == 'chain_of_thought_reasoning':
                    continue
                output_str += f"Table: {table}\n"
                output_str += "  Columns:\n"
                for column in columns:
                    output_str += f"    - {column}\n"
            output_str += "\n"
        
        return output_str

    def _cluster_equivalent_queries(self, pipeline_context: PipelineContext) -> List[List[SQLExecInfo]]:
        queries = pipeline_context.generated_sql_queries
        clusters = []
        visited = [False] * len(queries)

        for i in range(len(queries)):
            if visited[i]:
                continue
            
            current_cluster = [queries[i]]
            visited[i] = True
            
            for j in range(i + 1, len(queries)):
                if not visited[j]:
                    are_equivalent = compare_sqls_outcomes(
                        sql_1=queries[i].sql_exec_info.sql,
                        sql_2=queries[j].sql_exec_info.sql,
                        db_path=DatabaseConstants.DB_PATH,
                        engine=pipeline_context.db_engine
                    )
                    if are_equivalent:
                        current_cluster.append(queries[j])
                        visited[j] = True
            
            clusters.append(current_cluster)
            
        return clusters