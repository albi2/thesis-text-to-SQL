from pipeline.pipeline_step import PipelineStep
from context.pipeline_context import PipelineContext
from .executor.query_refinement_executor import QueryRefinementExecutor
from pipeline.pipeline_step_output import PipelineStepOutput
from pipeline.steps.sql_generation.executor.sql_generation_executor import SQLGenerationExecutor, SQLQuery
from util.db.execute import SQLExecInfo
from typing import List, Optional, Any

class QueryRefinementStepOutput(PipelineStepOutput):
    def __init__(self, generated_sql_queries: List[SQLQuery]):
        self.generated_sql_queries = generated_sql_queries

class QueryRefinementStep(PipelineStep[PipelineContext, QueryRefinementStepOutput]):
    def __init__(self):
        self.executor = QueryRefinementExecutor()

    def handle_execution(self, context: PipelineContext, previous_step_output: Optional[Any] = None) -> QueryRefinementStepOutput:
        print("------------------ QUERY REFINEMENT STEP ---------------------- \n")
        refined_queries = self.executor.execute(context)
        return QueryRefinementStepOutput(generated_sql_queries=refined_queries)