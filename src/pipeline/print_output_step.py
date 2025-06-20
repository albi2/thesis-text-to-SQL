from typing import Optional
from context.pipeline_context import PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.pipeline_step_output import PipelineStepOutput


class PrintOutputStep(PipelineStep[PipelineContext, None]):
    def handle_execution(self, context: PipelineContext, previous_step_output: Optional[PipelineStepOutput]) -> None:
        print("\n--- Information Retrieval Step Output ---")
        if previous_step_output:
            # Pretty print the dictionary
            import json
            print(json.dumps(previous_step_output.retrieved_context, indent=4))
        else:
            print("No output from previous step.")
        print("------------------------------------")
        return None