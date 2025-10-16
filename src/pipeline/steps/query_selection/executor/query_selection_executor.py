import re
import json
from typing import List
from components.models.reasoning_model_facade import ReasoningModelFacade
from context.pipeline_context import PipelineContext
from prompts.query_scoring import QUERY_SCORING_PROMPT
from prompts.query_comparison import QUERY_COMPARISON_PROMPT
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

        # Score and select top 5 queries
        scored_queries = self._score_queries(pipeline_context, generated_queries)
        
        # Sort by score and take the top 5
        sorted_queries = sorted(scored_queries, key=lambda x: x[0], reverse=True)
        top_queries = [query for score, query in sorted_queries[:5]]

        # Cluster the top 5 queries
        clusters = self._cluster_equivalent_queries_from_list(top_queries, pipeline_context)

        # Run tournament
        winning_query = self._run_tournament(clusters, pipeline_context)

        return winning_query


    def _score_queries(self, pipeline_context: PipelineContext, queries: List[SQLExecInfo]) -> List[tuple[int, SQLExecInfo]]:
        queries_str = "\n".join([q.sql_exec_info.sql for q in queries])
        schema = pipeline_context.schema_engine.ddl_schema.to_ddl(selected_tables=pipeline_context.unique_table_names, selected_columns=pipeline_context.unique_column_names)

        prompt_args = {
            "DATABASE_SCHEMA": schema,
            "QUESTION": pipeline_context.user_query,
            "HINT": getattr(pipeline_context, 'hint', ''),
            "QUERIES": queries_str,
        }

        full_prompt = QUERY_SCORING_PROMPT.format(**prompt_args)

        for attempt in range(self.MAX_RETRIES):
            model_response = self.api_model.invoke_chain(self.api_model.get_chain(), {"user_prompt": full_prompt})
            try:
                scored_queries = []
                for line in model_response.strip().split('\n'):
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        score = int(parts[0].strip())
                        query_sql = parts[1].strip()
                        # Find the corresponding SQLExecInfo object
                        for query_info in queries:
                            if query_info.sql_exec_info.sql == query_sql:
                                scored_queries.append((score, query_info))
                                break
                return scored_queries
            except (ValueError, IndexError) as e:
                print(f"Attempt {attempt + 1} failed: Could not parse scores from model response: {e}")

        return []

    def _run_tournament(self, clusters: List[List[SQLExecInfo]], pipeline_context: PipelineContext) -> SQLExecInfo:
        # Trim clusters to a maximum of two queries
        for i in range(len(clusters)):
            clusters[i] = clusters[i][:2]

        while len(clusters) > 1:
            # Round robin selection of two groups
            group1_idx, group2_idx = 0, 1
            
            group1 = clusters[group1_idx]
            group2 = clusters[group2_idx]

            champion1 = group1.pop(0)
            champion2 = group2.pop(0)

            winner = self._compare_queries(champion1, champion2, pipeline_context)

            if winner == 1:
                # champion1 wins, champion2 is out
                if group1: # if group1 has more champions, put the winner back
                    group1.insert(0, champion1)
                if not group2:
                    clusters.pop(group2_idx)
            else:
                # champion2 wins, champion1 is out
                if group2:
                    group2.insert(0, champion2)
                if not group1:
                    clusters.pop(group1_idx)
        
        return clusters[0][0]

    def _compare_queries(self, query1: SQLExecInfo, query2: SQLExecInfo, pipeline_context: PipelineContext) -> int:
        schema = pipeline_context.schema_engine.ddl_schema.to_ddl(selected_tables=pipeline_context.unique_table_names, selected_columns=pipeline_context.unique_column_names)
        
        prompt_args = {
            "DATABASE_SCHEMA": schema,
            "QUESTION": pipeline_context.user_query,
            "HINT": getattr(pipeline_context, 'hint', ''),
            "EVALUATION_CRITERIA": pipeline_context.query_evaluation_criteria,
            "QUERY_1": query1.sql_exec_info.sql,
            "QUERY_2": query2.sql_exec_info.sql,
        }

        full_prompt = QUERY_COMPARISON_PROMPT.format(**prompt_args)

        for attempt in range(self.MAX_RETRIES):
            model_response = self.api_model.invoke_chain(self.api_model.get_chain(), {"user_prompt": full_prompt})
            try:
                match = re.search(r"reasoning:(.*?)winner:\s*(\d+)", model_response, re.DOTALL)
                if match:
                    reasoning, winner = match.groups()
                    pipeline_context.query_comparison_reasoning = reasoning.strip()
                    return int(winner)
            except (ValueError, IndexError) as e:
                print(f"Attempt {attempt + 1} failed: Could not parse winner from model response: {e}")
        
        return 1 # Default to the first query in case of parsing failure

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
