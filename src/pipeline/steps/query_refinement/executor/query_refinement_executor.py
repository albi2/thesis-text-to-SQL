import re
import asyncio
from typing import List
from context.pipeline_context import PipelineContext
from prompts.query_refinement import PROMPT
from util.constants import DatabaseConstants
from components.models.api_model_facade import ApiModelFacade
from pipeline.steps.models.sql_query import SQLQuery
from util.db.execute import execute_sql_queries_async, SQLExecStatus

class QueryRefinementExecutor:
    def __init__(self):
        # It was 0.3
        self.api_model_gemini = ApiModelFacade(model_name="gemini-2.0-flash", temperature=0.2)

    def execute(self, pipeline_context: PipelineContext) -> List[SQLQuery]:
        if not hasattr(pipeline_context, 'non_executable_sql_queries') or not pipeline_context.non_executable_sql_queries:
            return

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        refined_queries_and_originals = loop.run_until_complete(
            self._refine_queries_concurrently(pipeline_context)
        )
        
        refined_sql_queries = [item[0] for item in refined_queries_and_originals]
        original_sql_queries = [item[1] for item in refined_queries_and_originals]

        if refined_sql_queries:
            pipeline_context.non_executable_sql_queries = []
            
            executable_sql_infos = loop.run_until_complete(
                execute_sql_queries_async(refined_sql_queries, DatabaseConstants.DB_PATH, pipeline_context.db_engine)
            )

            for original_query, sql_exec_info in zip(original_sql_queries, executable_sql_infos):
                if sql_exec_info.status == SQLExecStatus.CORRECT_SYNTAX:
                    pipeline_context.generated_sql_queries.append(SQLQuery(
                        sql_exec_info=sql_exec_info,
                        schema_representation=original_query.schema_representation,
                        model_key=original_query.model_key
                    ))
                    pipeline_context.fixed_sql_queries.append(SQLQuery(
                        sql_exec_info=sql_exec_info,
                        schema_representation=original_query.schema_representation,
                        model_key=original_query.model_key
                    ))
                else:
                    pipeline_context.non_executable_sql_queries.append(SQLQuery(
                        sql_exec_info=sql_exec_info,
                        schema_representation=original_query.schema_representation,
                        model_key=original_query.model_key
                    ))
        
        return refined_sql_queries

    async def _refine_queries_concurrently(self, pipeline_context: PipelineContext):
        tasks = []
        for sql_query in pipeline_context.non_executable_sql_queries:
            tasks.append(self._get_refined_query(pipeline_context, sql_query))
        
        return await asyncio.gather(*tasks)

    async def _get_refined_query(self, pipeline_context: PipelineContext, sql_query: SQLQuery):
        try:
            full_prompt = PROMPT.format(
                DATABASE_SCHEMA=sql_query.schema_representation.schema,
                QUESTION=pipeline_context.user_query,
                SQL_QUERY=sql_query.sql_exec_info.sql,
                ERROR_MESSAGE=sql_query.sql_exec_info.error_message,
                HINT=pipeline_context.task.evidence
            )
            
            query_chain = self.api_model_gemini.get_chain()
            model_response = await self.api_model_gemini.acall(query_chain, {"user_prompt": full_prompt})
            
            if "```sql" in model_response:
                query = re.sub(r"^\s+", "", model_response.split("```sql")[1].split("```")[0])
            elif "```" in model_response:
                query = model_response.split(";")[0].split("```")[0].strip() + ";"
            else:
                query = model_response
            
            return query, sql_query
        except Exception as e:
            print(f"Could not parse refined response from Gemini: {e}")
            return None, sql_query