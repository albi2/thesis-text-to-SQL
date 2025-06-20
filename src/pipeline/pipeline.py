from typing import TypeVar, Generic, Optional, Any

from context.generic_context import GenericContext
from pipeline.pipeline_step import PipelineStep

# Define a type variable for the generic pipeline context
C = TypeVar('C', bound=GenericContext)

class Pipeline(Generic[C]):
    """
    Represents a pipeline of steps executed in a chain.
    It holds the first step of the chain and initiates execution.
    It is generic over the Context type it operates on.
    Includes a nested Builder class for constructing the pipeline.
    """

    def __init__(self, first_step: Optional[PipelineStep[C, Any]]):
        """
        Initializes the Pipeline with the first step of the chain.

        Args:
            first_step: The first PipelineStep instance in the chain, or None if the pipeline is empty.
        """
        self._first_step = first_step

    def run(self, initial_context: C) -> None:
        """
        Runs the pipeline by executing the first step in the chain.
        The execution then proceeds through the linked steps.

        Args:
            initial_context: The initial context object.
        """
        if self._first_step:
            self._first_step.execute(initial_context, None)

    class Builder(Generic[C]):
        """
        Builds a Pipeline by chaining PipelineStep instances.
        It is generic over the Context type the pipeline operates on.
        This is a nested class of Pipeline.
        """

        def __init__(self):
            """
            Initializes the PipelineBuilder.
            """
            self._first_step: Optional[PipelineStep[C, Any]] = None
            self._last_step: Optional[PipelineStep[C, Any]] = None

        def add_step(self, step: PipelineStep[C, Any]) -> 'Pipeline.Builder[C]':
            """
            Adds a step to the pipeline chain.

            Args:
                step: The PipelineStep instance to add.

            Returns:
                The PipelineBuilder instance, allowing for chaining calls.
            """
            if not self._first_step:
                self._first_step = step
                self._last_step = step
            else:
                # Assuming PipelineStep has a link_with method
                self._last_step.link_with(step)
                self._last_step = step
            # DEBUG: Added step {step.__class__.__name__} to the pipeline builder.
            return self

        def build(self) -> 'Pipeline[C]':
            """
            Builds and returns the configured Pipeline instance.

            Returns:
                The built Pipeline instance.
            """
            # INFO: Building pipeline with first step: {self._first_step.__class__.__name__ if self._first_step else 'None'}
            return Pipeline(self._first_step)