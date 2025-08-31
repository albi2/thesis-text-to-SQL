from pipeline.steps.information_retrieval.information_retrieval_step import InformationRetrievalStepOutput
from pipeline.pipeline_step import PipelineStep
from pipeline.pipeline_step_output import PipelineStepOutput
from context.pipeline_context import PipelineContext
from pipeline.steps.schema_filter.executor.schema_filter_executor import SchemaFilterExecutor
from typing import Optional
import time 

class SchemaFilterStep(PipelineStep[PipelineContext, None]):
    def handle_execution(self,
                         pipeline_context: PipelineContext,
                         previous_step_output: InformationRetrievalStepOutput) -> Optional[PipelineStepOutput]:
        print("------------------ SCHEMA FILTER STEP ---------------------- \n")
        if len(pipeline_context.db_schema_per_keyword.keys()) == 0:
            print(f"Schema Filter step did not run successfully. Empty DB Schema")
            return None
        executor = SchemaFilterExecutor()
        result_dictionary = executor.execute(
            pipeline_context=pipeline_context
        )
        pipeline_context.selected_schema = result_dictionary

        return None