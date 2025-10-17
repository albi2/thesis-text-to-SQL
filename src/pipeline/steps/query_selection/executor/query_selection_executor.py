import re
import json
from typing import List
from components.models.reasoning_model_facade import ReasoningModelFacade
from context.pipeline_context import PipelineContext
from prompts.query_scoring import QUERY_SCORING_PROMPT, FEWSHOT_EXAMPLES
from prompts.query_comparison import QUERY_COMPARISON_PROMPT
from util.db.execute import SQLExecInfo, compare_sqls_outcomes
from util.constants import DatabaseConstants, Text2SQLModelKeys
from components.models.api_model_facade import ApiModelFacade
from pipeline.steps.models.sql_query import SQLQuery

class QuerySelectionExecutor:
    MAJORITY_THRESHOLD = 0.5
    MAX_RETRIES = 2
    MAX_QUERIES_PER_GROUP = 3

    def __init__(self):
        self.api_model = ApiModelFacade(model_name="gemini-2.5-flash-lite")

    def _prepare_relevant_entities(self, relevant_entities: dict) -> str:
        if not relevant_entities:
            return ""
        entities_by_phrase = {
            entity["phrase"]: entities_by_phrase.get(entity["phrase"], []) + [f"- {table}.{column} = {entity['value']}"]
            for table, columns in relevant_entities.items()
            for column, entities in columns.items()
            for entity in entities[:5]
        }
        return "\n\n".join([f"'{phrase}':\n" + "\n".join(entities) for phrase, entities in entities_by_phrase.items()]) + "\n\n"

    def execute(self, pipeline_context: PipelineContext) -> SQLQuery:
        generated_queries = pipeline_context.generated_sql_queries

        # Score and select top 5 queries
        scored_queries = self._score_queries(pipeline_context, generated_queries)
        pipeline_context.scoring = scored_queries

        if scored_queries:
            # Sort by score and take the top 5
            sorted_queries = sorted(scored_queries, key=lambda x: x.score, reverse=True)
            top_queries = sorted_queries[:5]

            # Cluster the top 5 queries
            clusters = self._cluster_equivalent_queries_from_list(top_queries, pipeline_context)
            print(f"CLUSTERS AFTER SCORING {clusters}")
        else:
            # If scoring fails, cluster all generated queries
            print(f"GENERATED QUERIES {generated_queries}")
            clusters = self._cluster_equivalent_queries_from_list(generated_queries, pipeline_context)
            print(f"CLUSTERS AFTER FAILED SCORING {clusters}")

        # Run tournament
        winning_query = self._run_tournament(clusters, pipeline_context)
        print(f"WINNER {winning_query}")

        return winning_query

    def _score_queries(self, pipeline_context: PipelineContext, queries: List[SQLQuery]) -> List[SQLQuery]:
        queries_str = "\n".join([f"{i+1}. {q.sql_exec_info.sql}" for i, q in enumerate(queries)])
        schema = pipeline_context.schema_engine.ddl_schema.to_ddl(selected_tables=pipeline_context.unique_table_names, selected_columns=pipeline_context.unique_column_names)

        prompt_args = {
            "DATABASE_SCHEMA": schema,
            "QUESTION": pipeline_context.user_query,
            "HINT": getattr(pipeline_context, 'hint', ''),
            "QUERIES": queries_str,
            "FEWSHOT_EXAMPLES": FEWSHOT_EXAMPLES,
            "EVALUATION_CRITERIA": pipeline_context.query_evaluation_criteria
        }

        
        prompt_args["PREVIOUS_PARSING_RESPONSE"] = ""
        for attempt in range(self.MAX_RETRIES):
            full_prompt = QUERY_SCORING_PROMPT.format(**prompt_args)

            model_response = self.api_model.call(self.api_model.get_chain(), {"user_prompt": full_prompt})
            print(f"SCORING MODEL RESPONSE {model_response}")
            try:
                # Extract JSON from code blocks if present
                json_match = re.search(r'```json\s*(.*?)\s*```', model_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to parse the entire response as JSON
                    json_str = model_response.strip()
                
                # Parse JSON
                parsed_response = json.loads(json_str)
                
                # Validate structure
                if "scores" not in parsed_response or not isinstance(parsed_response["scores"], list):
                    print(f"Attempt {attempt + 1}: Invalid JSON structure - missing 'scores' array")
                    continue
                
                for idx, score_obj in enumerate(parsed_response["scores"]):
                    if "score" not in score_obj:
                        continue
                    
                    if(idx >= len(queries)):
                        break

                    queries[idx].score = int(score_obj["score"])
                
                return queries
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1} failed: Could not parse JSON from model response: {e}")
                prompt_args["PREVIOUS_PARSING_RESPONSE"] = f"{e}"
            except (ValueError, KeyError) as e:
                print(f"Attempt {attempt + 1} failed: Error processing scores: {e}")
                prompt_args["PREVIOUS_PARSING_RESPONSE"] = f"{e}"

        # If all retries fail, return empty list
        print("All retry attempts exhausted. Returning empty scored queries list.")
        return []

    def _convert_score_to_elo(self, score: int) -> float:
        return float((score + 1) * 100)

    def _update_elo(self, elo1: float, elo2: float, result: int, k: int = 64) -> tuple[float, float]:
        e1 = 1 / (1 + 10**((elo2 - elo1) / 400))
        e2 = 1 - e1
        
        if result == 1:
            s1, s2 = 1, 0
        else:
            s1, s2 = 0, 1
            
        new_elo1 = elo1 + k * (s1 - e1)
        new_elo2 = elo2 + k * (s2 - e2)
        
        return new_elo1, new_elo2

    def _run_tournament(self, clusters: List[List[SQLQuery]], pipeline_context: PipelineContext) -> SQLQuery:
        if not clusters:
            return None

        representatives = [cluster[0] for cluster in clusters if cluster]
        
        if not representatives:
            return None
        
        if len(representatives) == 1:
            return representatives[0]

        # Initialize Elo ratings for each representative
        elos = {i: self._convert_score_to_elo(rep.score) for i, rep in enumerate(representatives)}

        # Round-robin tournament
        for i in range(len(representatives)):
            for j in range(i + 1, len(representatives)):
                winner = self._compare_queries(representatives[i], representatives[j], pipeline_context)
                
                # Update Elo ratings based on the match outcome
                elos[i], elos[j] = self._update_elo(elos[i], elos[j], winner)

        # Find the query with the highest Elo rating
        winner_index = max(elos, key=elos.get)
        return representatives[winner_index]

    def _compare_queries(self, query1: SQLQuery, query2: SQLQuery, pipeline_context: PipelineContext) -> int:
        schema = pipeline_context.schema_engine.ddl_schema.to_ddl(selected_tables=pipeline_context.unique_table_names, selected_columns=pipeline_context.unique_column_names)
        
        prompt_args = {
            "DATABASE_SCHEMA": schema,
            "QUESTION": pipeline_context.user_query,
            "HINT": getattr(pipeline_context, 'hint', ''),
            "EVALUATION_CRITERIA": pipeline_context.query_evaluation_criteria,
            "QUERY_1": query1.sql_exec_info.sql,
            "QUERY_2": query2.sql_exec_info.sql,
        }


        for attempt in range(self.MAX_RETRIES):
            full_prompt = QUERY_COMPARISON_PROMPT.format(**prompt_args)
            
            model_response = self.api_model.call(self.api_model.get_chain(), {"user_prompt": full_prompt})
            try:
                match = re.search(r"reasoning:(.*?)\s*winner:\s*(\d+)", model_response, re.DOTALL)
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

    def _cluster_equivalent_queries_from_list(self, queries: List[SQLQuery], pipeline_context: PipelineContext) -> List[List[SQLQuery]]:
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
