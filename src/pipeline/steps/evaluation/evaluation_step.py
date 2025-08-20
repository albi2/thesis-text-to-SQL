from typing import Optional, Any

from context.pipeline_context import PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.steps.evaluation.executor.evaluation_executor import EvaluationExecutor


class EvaluationStep(PipelineStep[PipelineContext, None]):
    def __init__(self):
        self.executor = EvaluationExecutor()

    def handle_execution(self, context: PipelineContext, previous_step_output: Optional[Any] = None) -> None:
        print("------------------ EVALUATION STEP ---------------------- \n")

        evaluation_result = self.executor.execute(
            pipeline_context=context
        )

        context.evaluation_result = evaluation_result

        return None