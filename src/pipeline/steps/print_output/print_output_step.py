from typing import Optional
from context.pipeline_context import PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.pipeline_step_output import PipelineStepOutput
import json

class PrintOutputStep(PipelineStep[PipelineContext, PipelineStepOutput]):
    def handle_execution(self, context: PipelineContext, previous_step_output: Optional[PipelineStepOutput]) -> Optional[PipelineStepOutput]:
        print("\n--- Information Retrieval Step Output ---")
        print(json.dumps(context, indent=4))
        print("------------------------------------")
        return previous_step_output