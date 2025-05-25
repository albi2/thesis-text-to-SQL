from context.pipeline_context import PipelineContext
from pipeline.pipeline_step import PipelineStep
from pipeline.simple_step_input import SimpleStepInput
# Assuming a basic logging setup exists or using print for demonstration
import logging

# Configure basic logging if not already set up
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NoOpPipelineStep(PipelineStep[PipelineContext, SimpleStepInput]):
    """
    A no-operation pipeline step for testing the pipeline structure.
    It logs its execution and passes the context through unchanged.
    """

    def __init__(self, name: str):
        """
        Initializes the NoOpPipelineStep with a name.

        Args:
            name: The name of the step for logging.
        """
        self.name = name
        # DEBUG: Initialized NoOpPipelineStep: {self.name}

    def before(self, context: PipelineContext) -> None:
        """Logs before execution."""
        logging.info(f"[{self.name}] Before execution.")
        super().before(context)

    def handle_execution(self, context: PipelineContext) -> None:
        """Logs execution and does nothing else."""
        logging.info(f"[{self.name}] Handling execution.")
        # Accessing input conceptually (though not used in NoOp)
        # input_data = SimpleStepInput(...) # Example of how input might be used
        # logging.info(f"[{self.name}] Conceptual input: {input_data}")
        pass # No operation performed on context

    def after(self, context: PipelineContext) -> None:
        """Logs after execution."""
        logging.info(f"[{self.name}] After execution.")
        super().after(context)