from pipeline.pipeline_step import PipelineStep
from context.pipeline_context import PipelineContext
from .executor.query_refinement_executor import QueryRefinementExecutor
from pipeline.pipeline_step_output import PipelineStepOutput
from pipeline.steps.sql_generation.executor.sql_generation_executor import SQLGenerationExecutor, SQLQuery
from util.db.execute import SQLExecInfo
from typing import List

class QueryRefinementStepOutput(PipelineStepOutput):
    def __init__(self, generated_sql_queries: List[SQLQuery]):
        self.generated_sql_queries = generated_sql_queries

class QueryRefinementStep(PipelineStep[PipelineContext, QueryRefinementStepOutput]):
    def __init__(self):
        self.executor = QueryRefinementExecutor()

    def execute(self, context: PipelineContext) -> QueryRefinementStepOutput:
        refined_queries = self.executor.execute(context)
        return QueryRefinementStepOutput(generated_sql_queries=refined_queries)