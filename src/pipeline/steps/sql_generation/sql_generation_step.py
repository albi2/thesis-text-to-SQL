from typing import Optional, Any, List
from context.pipeline_context import PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.pipeline_step_output import PipelineStepOutput
from pipeline.steps.sql_generation.executor.sql_generation_executor import SQLGenerationExecutor
from util.db.execute import SQLExecInfo

class SQLGenerationStepOutput(PipelineStepOutput):
    def __init__(self, generated_sql_queries: List[SQLExecInfo]):
        self.generated_sql_queries = generated_sql_queries

class SQLGenerationStep(PipelineStep[PipelineContext, SQLGenerationStepOutput]):
    def __init__(self):
        self.executor = SQLGenerationExecutor()

    def handle_execution(self, context: PipelineContext, previous_step_output: Optional[Any] = None) -> Optional[SQLGenerationStepOutput]:
        print("------------------ SQL GENERATION STEP ---------------------- \n")
        
        generated_queries = self.executor.execute(
            pipeline_context=context
        )
        context.generated_sql_queries = generated_queries
        
        return SQLGenerationStepOutput(generated_sql_queries=generated_queries)