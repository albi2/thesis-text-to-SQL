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
        
        queries_by_model = {}
        for sql_query in pipeline_context.non_executable_sql_queries:
            if sql_query.model_key not in queries_by_model:
                queries_by_model[sql_query.model_key] = []
            queries_by_model[sql_query.model_key].append(sql_query)

        model_facades = {
            Text2SQLModelKeys.XIYAN: self.text2sql_model_facade,
            Text2SQLModelKeys.DEFOG: self.defog_text2sql_model_facade,
            Text2SQLModelKeys.OMNI: self.omni_text2sql_model_facade,
            Text2SQLModelKeys.GEMINI: self.api_model_gemini
        }

        for model_key, queries in queries_by_model.items():
            model_facade = model_facades.get(model_key)
            if not model_facade:
                continue

            try:
                if isinstance(model_facade, Text2SQLModelFacade):
                    model_facade.load_model_and_tokenizer()

                for sql_query in queries:
                    full_prompt = PROMPT.format(
                        DATABASE_SCHEMA=sql_query.schema_representation.schema,
                        QUESTION=pipeline_context.user_query,
                        SQL_QUERY=sql_query.sql_exec_info.sql,
                        ERROR_MESSAGE=sql_query.sql_exec_info.error_message
                    )
                    
                    try:
                        if isinstance(model_facade, ApiModelFacade):
                            query_chain = model_facade.get_chain()
                            model_response = model_facade.invoke_chain(query_chain, {"user_prompt": full_prompt})
                        else:
                            model_response = model_facade.query(full_prompt)
                        
                        if "```sql" in model_response:
                            query = re.sub(r"^\s+", "", model_response.split("```sql")[1].split("```")[0])
                        elif "```" in model_response:
                            query = model_response.split(";")[0].split("```")[0].strip() + ";"
                        else:
                            query = model_response
                        
                        refined_sql_queries.append(query)
                        original_sql_queries.append(sql_query)
                    except Exception as e:
                        print(f"Could not parse refined response from {model_key}: {e}")

            except Exception as e:
                print(f"Failed to process model {model_key}: {e}")
            finally:
                if isinstance(model_facade, Text2SQLModelFacade):
                    model_facade.unload_model()

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