import re
import asyncio
from typing import List
from components.models.text2sql_model_facade import Text2SQLModelFacade
from context.pipeline_context import PipelineContext
from prompts.query_refinement import PROMPT
from util.constants import HuggingFaceModelConstants, Text2SQLModelKeys, DatabaseConstants
from components.models.api_model_facade import ApiModelFacade
from pipeline.steps.models.sql_query import SQLQuery
from util.db.execute import execute_sql_queries_async, SQLExecStatus

class QueryRefinementExecutor:
    def __init__(self):
        self.text2sql_model_facade = Text2SQLModelFacade()
        self.omni_text2sql_model_facade = Text2SQLModelFacade(model_name=HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_PATH, model_repo=HuggingFaceModelConstants.OMNI_TEXT2SQL_MODEL_REPO)
        self.defog_text2sql_model_facade = Text2SQLModelFacade(model_name=HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_PATH, model_repo=HuggingFaceModelConstants.DEFOG_TEXT2SQL_MODEL_REPO)
        self.api_model_gemini = ApiModelFacade(model_name="gemini-2.5-flash")

    def execute(self, pipeline_context: PipelineContext) -> List[SQLQuery]:
        if not hasattr(pipeline_context, 'non_executable_sql_queries') or not pipeline_context.non_executable_sql_queries:
            return

        refined_sql_queries = []
        original_sql_queries = []

        for sql_query in pipeline_context.non_executable_sql_queries:
            model_key = sql_query.model_key
            schema_representation = sql_query.schema_representation
            
            full_prompt = PROMPT.format(
                DATABASE_SCHEMA=schema_representation.schema,
                QUESTION=pipeline_context.user_query,
                SQL_QUERY=sql_query.sql_exec_info.sql,
                ERROR_MESSAGE=sql_query.sql_exec_info.error_message
            )

            model_response = None
            if model_key == Text2SQLModelKeys.GEMINI:
                query_chain = self.api_model_gemini.get_chain()
                model_response = query_chain.invoke({"user_prompt": full_prompt})
            elif model_key == Text2SQLModelKeys.XIYAN:
                model_response = self.text2sql_model_facade.query(full_prompt)
            elif model_key == Text2SQLModelKeys.OMNI:
                model_response = self.omni_text2sql_model_facade.query(prompt=full_prompt, system_prompt=None, max_new_tokens=1024)
            elif model_key == Text2SQLModelKeys.DEFOG:
                model_response = self.defog_text2sql_model_facade.query(prompt=full_prompt, system_prompt=None, max_new_tokens=1024)

            if model_response:
                try:
                    if "```sql" in model_response:
                        query = re.sub(r"^\s+", "", model_response.split("```sql")[1].split("```")[0])
                    elif "```" in model_response:
                        query = model_response.split(";")[0].split("```")[0].strip() + ";"
                    else:
                        query = model_response
                    
                    refined_sql_queries.append(query)
                    original_sql_queries.append(sql_query)
                except Exception as e:
                    print(f"Could not parse refined response: {e}")
        
        if refined_sql_queries:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

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
        
        return refined_sql_queries