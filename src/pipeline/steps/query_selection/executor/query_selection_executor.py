import re
from typing import List
from components.models.reasoning_model_facade import ReasoningModelFacade
from context.pipeline_context import PipelineContext
from prompts.query_selection import PROMPT
from util.db.execute import SQLExecInfo, compare_sqls_outcomes
from util.constants import DatabaseConstants, Text2SQLModelKeys
from components.models.api_model_facade import ApiModelFacade

class QuerySelectionExecutor:
    def __init__(self):
        # self.reasoning_model_facade = ReasoningModelFacade()
        self.api_model = ApiModelFacade()

    def execute(self, pipeline_context: PipelineContext) -> SQLExecInfo:
        clusters = self._cluster_equivalent_queries(pipeline_context)
        
        # total_queries = len(pipeline_context.generated_sql_queries)
        # majority_threshold = total_queries / 2
        
        # selected_queries = []
        # majority_cluster = next((cluster for cluster in clusters if len(cluster) > majority_threshold), None)

        # if majority_cluster:
        #     selected_queries = majority_cluster
        # else:
        #     model_priority = {
        #         model: config["priority"]
        #         for model, config in Text2SQLModelKeys.TEXT2SQL_MODEL_CONFIGS.items()
        #     }
        #     for cluster in clusters:
        #         best_query = min(cluster, key=lambda query: model_priority.get(query.model_key, 99))
        #         selected_queries.append(best_query)
        
        model_priority = {
            model: config["priority"]
            for model, config in Text2SQLModelKeys.TEXT2SQL_MODEL_CONFIGS.items()
        }
        
        selected_queries = []
        for cluster in clusters:
            best_query_in_cluster = min(cluster, key=lambda query: model_priority.get(query.model_key, 99))
            selected_queries.append(best_query_in_cluster)

        queries_with_results = ""
        for i, info in enumerate(selected_queries):
            queries_with_results += f"{i}: {info.sql_exec_info.sql}\n"
            queries_with_results += f"  Execution Status: {info.sql_exec_info.status.value}\n"
            if info.sql_exec_info.result is not None:
                queries_with_results += f"  Query Output: {str(info.sql_exec_info.result)}\n"

        if not hasattr(pipeline_context, 'schema_engine') or pipeline_context.schema_engine is None:
            raise ValueError("SchemaEngine not found in pipeline context.")

        mschema_string: str = pipeline_context.schema_engine.mschema.to_mschema(
            show_type_detail=True
        )

        full_prompt = PROMPT.format(
            DATABASE_SCHEMA=mschema_string,
            QUESTION=pipeline_context.user_query,
            HINT=getattr(pipeline_context, 'hint', ''),
            QUERIES=queries_with_results
        )

        query_chain = self.api_model.get_chain()
        model_response = self.api_model.invoke_chain(query_chain, {"user_prompt": full_prompt})

        try:
            match = re.search(r"query_index:\s*(\d+)", model_response)
            if match:
                query_index = int(match.group(1))
                return selected_queries[query_index]
        except (ValueError, IndexError) as e:
            print(f"Could not parse query index from model response: {e}")
            if selected_queries:
                return selected_queries[0]
        
        if selected_queries:
            return selected_queries[0]
        
        return None

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