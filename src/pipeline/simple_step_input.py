from pipeline.pipeline_step_input import PipelineStepInput

class SimpleStepInput(PipelineStepInput):
    """
    A simple concrete implementation of PipelineStepInput for testing.
    """
    def __init__(self, message: str = "default"):
        self.message = message

    def __repr__(self) -> str:
        return f"SimpleStepInput(message='{self.message}')"