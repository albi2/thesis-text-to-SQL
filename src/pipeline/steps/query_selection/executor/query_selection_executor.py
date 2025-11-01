import re
import json
import asyncio
import random
import numpy as np
from typing import List, Any
from components.models.reasoning_model_facade import ReasoningModelFacade
from context.pipeline_context import PipelineContext
from prompts.query_scoring import QUERY_SCORING_PROMPT, FEWSHOT_EXAMPLES
from prompts.query_comparison import QUERY_COMPARISON_PROMPT, NOCRITERIA_COMPARISON_FEWSHOTS
from prompts.query_selection import PROMPT as QUERY_SELECTION_PROMPT
from util.db.execute import compare_sqls_outcomes
from util.constants import DatabaseConstants
from components.models.api_model_facade import ApiModelFacade
from pipeline.steps.models.sql_query import SQLQuery
from pipeline.steps.models.schema_representation import SchemaRepresentation, SchemaFormat, SchemaType
import copy

class QuerySelectionExecutor:
    MAJORITY_THRESHOLD = 0.5
    MAX_RETRIES = 2
    MAX_QUERIES_PER_GROUP = 3

    def __init__(self):
        self.api_model = ApiModelFacade(model_name="gemini-2.5-flash-lite")

    def _prepare_relevant_entities(self, relevant_entities: dict) -> str:
        """
        Formats the relevant entities into a readable string, limiting them to 3 per phrase.
        """
        if not relevant_entities:
            return ""

        entities_by_phrase = {}
        for table, columns in relevant_entities.items():
            for column, entities in columns.items():
                for entity in entities[:3]:
                    phrase = entity["phrase"]
                    if phrase not in entities_by_phrase:
                        entities_by_phrase[phrase] = []
                    entities_by_phrase[phrase].append(f"- {table}.{column} = {entity['value']}")

        output_str = ""
        for phrase, entities in entities_by_phrase.items():
            output_str += f"'{phrase}':\n"
            output_str += "\n".join(entities)
            output_str += "\n\n"
        
        return output_str

    def execute(self, pipeline_context: PipelineContext) -> SQLQuery:
        queries = pipeline_context.generated_sql_queries
        clusters = self._cluster_equivalent_queries_from_list(queries, pipeline_context)

        loop = asyncio.get_event_loop()

        # Score queries before selection tasks
        scored_queries = loop.run_until_complete(self._shuffle_batched_scoring(pipeline_context, pipeline_context.generated_sql_queries))

        # Run selection tasks
        tasks = [
            self.select_by_scoring(pipeline_context, clusters, scored_queries),
            self.select_by_singleprompt(pipeline_context, clusters)
        ]
        scoring_winner, singleprompt_winner = loop.run_until_complete(asyncio.gather(*tasks))

        pipeline_context.winning_queries = [scoring_winner, singleprompt_winner]

        if scoring_winner and singleprompt_winner:
            are_equivalent = compare_sqls_outcomes(
                sql_1=scoring_winner.sql_exec_info.sql,
                sql_2=singleprompt_winner.sql_exec_info.sql,
                db_path=DatabaseConstants.DB_PATH,
                engine=pipeline_context.db_engine
            )
            if are_equivalent:
                return scoring_winner
            # else:
            #     winner = self._compare_queries(scoring_winner, singleprompt_winner, pipeline_context)
            #     if winner == 1:
            #         return scoring_winner
                
            #     return singleprompt_winner
            else:
                return max([scoring_winner, singleprompt_winner], key=lambda query: query.cluster_size)
            # else:
            #     return return max([scoring_winner, singleprompt_winner], key=lambda query: query.score)
        elif scoring_winner:
            return scoring_winner
        elif singleprompt_winner:
            return singleprompt_winner
        else:
            return None

    async def select_by_singleprompt(self, pipeline_context: PipelineContext, clusters: List[List[SQLQuery]]) -> SQLQuery:
        # model_priority = {
        #     model: config["priority"]
        #     for model, config in Text2SQLModelKeys.TEXT2SQL_MODEL_CONFIGS.items()
        # }
        selected_queries = []
        for cluster in clusters:
            best_query_in_cluster = max(cluster, key=lambda query: query.score)
            selected_queries.append(best_query_in_cluster)
            # selected_queries.append(cluster[0])

        queries_with_results = ""
        for i, info in enumerate(selected_queries):
            # cluster_size = len([q for q in queries if compare_sqls_outcomes(q.sql_exec_info.sql, info.sql_exec_info.sql, DatabaseConstants.DB_PATH, pipeline_context.db_engine)])
            queries_with_results += f"{i}: {info.sql_exec_info.sql}\n"
            queries_with_results += f"  Execution Status: {info.sql_exec_info.status.value}\n"
            if info.sql_exec_info.result is not None:
                queries_with_results += f"  Query Output: {str(info.sql_exec_info.result)}\n"
            # queries_with_results += f"  Votes: {cluster_size}\n"

        if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
            raise ValueError("SchemaEngine not found in pipeline context.")

        mschema_string: str = pipeline_context.schema_engine.mschema.to_mschema(
            selected_tables=pipeline_context.unique_table_names, selected_columns=pipeline_context.unique_column_names
        )

        filtered_schemas_str = self._prepare_filtered_schemas(pipeline_context.selected_schemas)
        relevant_entities_str = self._prepare_relevant_entities(pipeline_context.relevant_entities)
        full_prompt = QUERY_SELECTION_PROMPT.format(
            DATABASE_SCHEMA=mschema_string,
            FILTERED_SCHEMAS=filtered_schemas_str,
            QUESTION=pipeline_context.user_query,
            HINT=getattr(pipeline_context, 'hint', ''),
            CRITERIA=pipeline_context.query_evaluation_criteria,
            QUERIES=queries_with_results,
            RELEVANT_ENTITIES=relevant_entities_str
        )
        
        query_chain = self.api_model.get_chain()
        model_response = await self.api_model.acall(query_chain, {"user_prompt": full_prompt})

        try:
            match = re.search(r"reasoning:\s*(.*?)\s*query_index:\s*(\d+)", model_response, re.DOTALL)
            if match:
                reasoning = match.group(1).strip()
                query_index = int(match.group(2))
                pipeline_context.query_selection_reasoning = reasoning
                return selected_queries[query_index]
            else:
                pipeline_context.query_selection_reasoning = model_response
                print(f"Could not parse query index from selection response: {model_response}")
        except (ValueError, IndexError) as e:
            print(f"Could not parse query index or reasoning from model response: {e}")
            pipeline_context.query_selection_reasoning = model_response
            if selected_queries:
                return max(selected_queries, key=lambda query: query.cluster_size)
        
        if selected_queries:
            return max(selected_queries, key=lambda query: query.cluster_size)
        
        return None

    async def select_by_scoring(self, pipeline_context: PipelineContext, clusters: List[List[SQLQuery]], scored_queries: List[SQLQuery]) -> SQLQuery:

        selected_queries = []
        for cluster in clusters:
            # best_query_in_cluster = max(cluster, key=lambda query: query.score)
            best_query_in_cluster = max(cluster, key=lambda query: query.score)
            selected_queries.append(best_query_in_cluster)
            # selected_queries.append(cluster[0])
        if scored_queries:
            # Cluster the top 5 queries
            narrowed_down_clusters = self._cluster_equivalent_queries_from_list(selected_queries, pipeline_context, update_context_size=False)
            print(f"CLUSTERS AFTER SCORING {narrowed_down_clusters}")
        else:
            # If scoring fails, cluster all generated queries
            print(f"GENERATED QUERIES FROM EACH CLUSTER {selected_queries}")
            narrowed_down_clusters = self._cluster_equivalent_queries_from_list(selected_queries, pipeline_context, update_context_size=False)
            print(f"CLUSTERS AFTER FAILED SCORING {narrowed_down_clusters}")

        # Run tournament
        winning_query = self._run_elo_tournament(narrowed_down_clusters, pipeline_context)

        return winning_query

    async def _score_single_query(self, query: SQLQuery, pipeline_context: PipelineContext):
        relevant_entities_str = self._prepare_relevant_entities(pipeline_context.relevant_entities)
        prompt_args = {
            "DATABASE_SCHEMA": query.schema_representation.schema,
            "QUESTION": pipeline_context.user_query,
            "HINT": getattr(pipeline_context, 'hint', ''),
            "QUERY": query.sql_exec_info.sql,
            "QUERY_OUTPUT": query.sql_exec_info.result,
            "FEWSHOT_EXAMPLES": FEWSHOT_EXAMPLES,
            "RELEVANT_ENTITIES": relevant_entities_str
            # "EVALUATION_CRITERIA": pipeline_context.query_evaluation_criteria
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                full_prompt = QUERY_SCORING_PROMPT.format(**prompt_args)

                chain = self.api_model.get_chain()
                model_response = await self.api_model.acall(chain, {"user_prompt": full_prompt})

                print(f"SCORING RESPONSE {model_response}")

                json_match = re.search(r'```json\s*(.*?)\s*```', model_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = model_response.strip()
                
                parsed_response = json.loads(json_str)
                
                if "score" in parsed_response:
                    query.score = int(parsed_response["score"])
                if "chain_of_thought" in parsed_response:
                    query.score_cot = parsed_response["chain_of_thought"]
                
                return query
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1} for query failed: Could not parse JSON from model response: {e}")
            except (ValueError, KeyError) as e:
                print(f"Attempt {attempt + 1} for query failed: Error processing score: {e}")
            except Exception as e:
                print(f"Attempt {attempt + 1} for query failed: Error generating score: {e}")
        
        query.score = 1
        return query

    async def _score_batch(self, batch: List[SQLQuery], pipeline_context: PipelineContext) -> List[tuple[str, int]]:
        batch_queries_str = ""
        for i, query in enumerate(batch):
            batch_queries_str += f"{i}: {query.sql_exec_info.sql}\n"
            if query.sql_exec_info.result is not None:
                batch_queries_str += f"  Query Output:\n {str(query.sql_exec_info.result)}\n"

        merged_schema = self._merge_schemas_for_batch(batch, pipeline_context)
        relevant_entities_str = self._prepare_relevant_entities(pipeline_context.relevant_entities)
        prompt_args = {
            "DATABASE_SCHEMA": merged_schema,
            "QUESTION": pipeline_context.user_query,
            "HINT": getattr(pipeline_context, 'hint', ''),
            "QUERIES": batch_queries_str,
            "FEWSHOT_EXAMPLES": FEWSHOT_EXAMPLES,
            "RELEVANT_ENTITIES": relevant_entities_str
        }

        full_prompt = QUERY_SCORING_PROMPT.format(**prompt_args)
        batch_scores = []

        for attempt in range(self.MAX_RETRIES):
            try:
                chain = self.api_model.get_chain()
                model_response = await self.api_model.acall(chain, {"user_prompt": full_prompt})

                json_match = re.search(r'```json\s*(.*?)\s*```', model_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = model_response.strip()

                parsed_scores = json.loads(json_str)

                if len(parsed_scores) != len(batch):
                    print(f"Attempt {attempt + 1} for batch failed: Number of scores ({len(parsed_scores)}) does not match batch size ({len(batch)}).")
                    continue

                for i, score_info in enumerate(parsed_scores):
                    sql = batch[i].sql_exec_info.sql
                    score = int(score_info.get("score", 0))
                    batch_scores.append((sql, score))
                return batch_scores
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Attempt {attempt + 1} for batch failed: Error parsing scores: {e}")
            except Exception as e:
                print(f"Attempt {attempt + 1} for batch failed: Error generating scores: {e}")
        return []

    async def _shuffle_batched_scoring(self, pipeline_context: PipelineContext, queries: List[SQLQuery], m: int = 10, k: int = 7) -> List[SQLQuery]:
        query_scores = {query.sql_exec_info.sql: [] for query in queries}
        
        tasks = []
        for _ in range(m):
            random.shuffle(queries)
            batches = [queries[i:i + k] for i in range(0, len(queries), k)]
            for batch in batches:
                tasks.append(self._score_batch(batch, pipeline_context))

        results = await asyncio.gather(*tasks)

        for batch_result in results:
            for sql, score in batch_result:
                if sql in query_scores:
                    query_scores[sql].append(score)

        for query in queries:
            scores = query_scores[query.sql_exec_info.sql]
            if scores:
                query.score = np.mean(scores)
            else:
                query.score = 0.0
        return queries

    def _score_queries(self, pipeline_context: PipelineContext, queries: List[SQLQuery]) -> List[Any]:
        print(f"LEN OF QUERIES TO BE SCORED {len(queries)}")
        tasks = [self._score_single_query(query, pipeline_context) for query in queries]
        return asyncio.gather(*tasks)

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

    def _run_point_tournament(self, clusters: List[List[SQLQuery]], pipeline_context: PipelineContext) -> SQLQuery:
        if not clusters:
            return None

        representatives = [cluster[0] for cluster in clusters if cluster]
        
        if not representatives:
            return None
        
        if len(representatives) == 1:
            return representatives[0]

        scores = {i: 0 for i in range(len(representatives))}

        for i in range(len(representatives)):
            for j in range(i + 1, len(representatives)):
                winner = self._compare_queries(representatives[i], representatives[j], pipeline_context)
                if winner == 1:
                    scores[i] += 1
                else:
                    scores[j] += 1
        
        winner_index = max(scores, key=scores.get)
        return representatives[winner_index]

    def _run_elo_tournament(self, clusters: List[List[SQLQuery]], pipeline_context: PipelineContext) -> SQLQuery:
        if not clusters:
            return None

        representatives = [cluster[0] for cluster in clusters]
        
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
        max_elo = max(elos.values())
        top_indices = [i for i, e in elos.items() if e == max_elo]

        if len(top_indices) == 1:
            return representatives[top_indices[0]]
        else:
            # tie → pick by cluster size
            return max((representatives[i] for i in top_indices), key=lambda q: q.cluster_size)

    def _compare_queries(self, query1: SQLQuery, query2: SQLQuery, pipeline_context: PipelineContext) -> int:
        schema = self._merge_schemas(query1.schema_representation, query2.schema_representation, pipeline_context)
        relevant_entities_str = self._prepare_relevant_entities(pipeline_context.relevant_entities)

        prompt_args = {
            "DATABASE_SCHEMA": schema,
            "QUESTION": pipeline_context.user_query,
            "HINT": getattr(pipeline_context, 'hint', ''),
            # "EVALUATION_CRITERIA": pipeline_context.query_evaluation_criteria,
            "QUERY_1": f"{query1.sql_exec_info.sql}",
            "QUERY_1_OUTPUT": f"{query1.sql_exec_info.result}",
            "QUERY_2": f"{query2.sql_exec_info.sql}",
            "QUERY_2_OUTPUT": f"{query2.sql_exec_info.result}",
            "FEWSHOT_EXAMPLES": NOCRITERIA_COMPARISON_FEWSHOTS,
            "RELEVANT_ENTITIES": relevant_entities_str
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                full_prompt = QUERY_COMPARISON_PROMPT.format(**prompt_args)
                model_response = self.api_model.call(self.api_model.get_chain(), {"user_prompt": full_prompt})

                json_match = re.search(r'```json\s*(.*?)\s*```', model_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = model_response.strip()
                
                parsed_response = json.loads(json_str)

                print(f"QUERY COMPARISON BETWEEN {query1.sql_exec_info.result} and {query2.sql_exec_info.result} yields {model_response}")
                
                if "winner" in parsed_response:
                    return int(parsed_response["winner"])
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Attempt {attempt + 1} failed: Could not parse winner from model response: {e}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: Could not generate response: {e}")
        
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

    def _cluster_equivalent_queries_from_list(self, queries: List[SQLQuery], pipeline_context: PipelineContext, update_context_size: bool = True) -> List[List[SQLQuery]]:
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
            
            if update_context_size:
                for query in current_cluster:
                    query.cluster_size = len(current_cluster)
            clusters.append(current_cluster)
            
        return clusters

    def _merge_schemas_for_batch(self, batch: List[SQLQuery], pipeline_context: PipelineContext) -> str:
        merged_tables = set()
        merged_columns = set()

        for query in batch:
            merged_tables.update(query.schema_representation.selected_tables)
            merged_columns.update(query.schema_representation.selected_columns)

        return pipeline_context.schema_engine.ddl_schema.to_ddl(selected_tables=list(merged_tables), selected_columns=list(merged_columns))

    def _merge_schemas(self, schema1: SchemaRepresentation, schema2: SchemaRepresentation, pipeline_context: PipelineContext):
        schema1_tables = set(schema1.selected_tables)
        schema1_columns = set(schema1.selected_columns)

        schema2_tables = set(schema2.selected_tables)
        schema2_columns = set(schema2.selected_columns)

        merged_tables = schema1_tables.union(schema2_tables)
        merged_columns = schema1_columns.union(schema2_columns)

        return pipeline_context.schema_engine.ddl_schema.to_ddl(selected_tables=merged_tables, selected_columns=merged_columns)
