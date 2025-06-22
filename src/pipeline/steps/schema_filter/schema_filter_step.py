from pipeline.steps.information_retrieval.information_retrieval_step import InformationRetrievalStepOutput
from src.pipeline.pipeline_step import PipelineStep
from src.pipeline.pipeline_step_output import PipelineStepOutput
from src.context.pipeline_context import PipelineContext
from src.pipeline.steps.schema_filter.executor.schema_filter_executor import SchemaFilterExecutor
from typing import Optional

class SchemaFilterStep(PipelineStep[PipelineContext, None]):
    def handle_execution(self,
                         pipeline_context: PipelineContext,
                         previous_step_output: InformationRetrievalStepOutput) -> Optional[PipelineStepOutput]:
        
        executor = SchemaFilterExecutor()
        result_dictionary = executor.execute(
            pipeline_context=pipeline_context
        )
        pipeline_context.selected_schema = result_dictionary
        
        return None