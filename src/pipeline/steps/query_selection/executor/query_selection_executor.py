import re
import json
from typing import List
from components.models.reasoning_model_facade import ReasoningModelFacade
from context.pipeline_context import PipelineContext
from prompts.query_selection import PROMPT as QUERY_SELECTION_PROMPT
from prompts.query_selection_second_round import PROMPT as QUERY_SELECTION_SECOND_ROUND_PROMPT
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
        generated_queries = pipeline_context.generated_sql_queries

        # First selection round
        selected_indices = self._select_queries(pipeline_context, generated_queries)
        
        if not selected_indices:
            print("No queries selected in the first round. Returning the first generated query.")
            return generated_queries[0] if generated_queries else None

        selected_queries = [generated_queries[i] for i in selected_indices]

        # Check for result equality
        clusters = self._cluster_equivalent_queries_from_list(selected_queries, pipeline_context)

        if len(clusters) == 1:
            # All queries have the same result
            return self._select_final_query(clusters, pipeline_context)

        # Second selection round if results are not equal
        print("Query results are not equal, performing second selection round.")
        
        queries_from_first_round = [q for cluster in clusters for q in cluster]
        selected_indices_2 = self._select_queries(pipeline_context, generated_queries, is_second_round=True, previous_selection=queries_from_first_round)
        
        if not selected_indices_2:
            print("No queries selected in the second round. Falling back to clustering.")
            final_clusters = self._cluster_equivalent_queries_from_list(selected_queries, pipeline_context)
            return self._select_final_query(final_clusters, pipeline_context)

        selected_queries_2 = [generated_queries[i] for i in selected_indices_2]
        
        final_clusters = self._cluster_equivalent_queries_from_list(selected_queries_2, pipeline_context)
        
        return self._select_final_query(final_clusters, pipeline_context)

    def _select_final_query(self, clusters, pipeline_context):
        if not clusters:
            return pipeline_context.generated_sql_queries[0]

        biggest_cluster = max(clusters, key=len)
        
        original_clusters = self._cluster_equivalent_queries(pipeline_context)
        original_biggest_cluster = max(original_clusters, key=len)

        for query in biggest_cluster:
            if query in original_biggest_cluster:
                return query
        
        return biggest_cluster[0]

    def _select_queries(self, pipeline_context: PipelineContext, queries: List[SQLExecInfo], is_second_round: bool = False, previous_selection: List[SQLExecInfo] = None) -> List[int]:
        queries_with_results = ""
        for i, info in enumerate(queries):
            queries_with_results += f"{i}: {info.sql_exec_info.sql}\n"
            queries_with_results += f"  Execution Status: {info.sql_exec_info.status.value}\n"
            if info.sql_exec_info.result is not None:
                queries_with_results += f"  Query Output: {str(info.sql_exec_info.result)}\n"

        mschema_string = pipeline_context.schema_engine.mschema.to_mschema(show_type_detail=True)
        filtered_schemas_str = self._prepare_filtered_schemas(pipeline_context.selected_schemas)
        
        prompt_template = QUERY_SELECTION_SECOND_ROUND_PROMPT if is_second_round else QUERY_SELECTION_PROMPT
        
        prompt_args = {
            "DATABASE_SCHEMA": mschema_string,
            "FILTERED_SCHEMAS": filtered_schemas_str,
            "QUESTION": pipeline_context.user_query,
            "HINT": getattr(pipeline_context, 'hint', ''),
            "CRITERIA": pipeline_context.query_evaluation_criteria,
            "QUERIES": queries_with_results
        }

        if is_second_round and previous_selection:
            previous_selection_str = ""
            for info in previous_selection:
                # Find the index of the query in the main list
                try:
                    previous_selection_str += f"{info.sql_exec_info.sql}\n"
                    previous_selection_str += f"  Execution Status: {info.sql_exec_info.status.value}\n"
                    if info.sql_exec_info.result is not None:
                        previous_selection_str += f"  Query Output: {str(info.sql_exec_info.result)}\n"
                except ValueError:
                    # Should not happen if logic is correct
                    pass
            prompt_args["PREVIOUS_SELECTION"] = previous_selection_str

        full_prompt = prompt_template.format(**prompt_args)

        for attempt in range(self.MAX_RETRIES):
            model_response = self.api_model.invoke_chain(self.api_model.get_chain(), {"user_prompt": full_prompt})
            try:
                match = re.search(r"reasoning:\s*(.*?)\s*query_indices:\s*(\[.*?\])", model_response, re.DOTALL)
                if match:
                    reasoning, indices_str = match.groups()
                    indices = json.loads(indices_str)
                    pipeline_context.query_selection_reasoning = reasoning.strip()
                    return [int(i) for i in indices]
            except (ValueError, IndexError, json.JSONDecodeError) as e:
                print(f"Attempt {attempt + 1} failed: Could not parse query indices or reasoning from model response: {e}")
                pipeline_context.query_selection_reasoning = model_response
        
        return []

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

    def _cluster_equivalent_queries_from_list(self, queries: List[SQLExecInfo], pipeline_context: PipelineContext) -> List[List[SQLExecInfo]]:
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

    def _cluster_equivalent_queries(self, pipeline_context: PipelineContext) -> List[List[SQLExecInfo]]:
        return self._cluster_equivalent_queries_from_list(pipeline_context.generated_sql_queries, pipeline_context)