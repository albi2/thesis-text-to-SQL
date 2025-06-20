from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any

from context.generic_context import GenericContext
from pipeline.pipeline_step_output import PipelineStepOutput

# Define type variables for the generic step
C = TypeVar('C', bound=GenericContext)
O = TypeVar('O', bound=PipelineStepOutput)
I = TypeVar('I', bound=Optional[PipelineStepOutput])

class PipelineStep(ABC, Generic[C, O]):
    """
    Abstract base class for a step in a pipeline, implementing the
    Chain of Responsibility pattern. Each step processes a context
    and can pass it to the next step in the chain.
    It is generic over the Context type (C) and the Output type (O)
    that the step conceptually produces.
    Includes before, after, handle_execution, and should_execute methods.
    """

    _next_step: Optional['PipelineStep[C, Any]'] = None

    def link_with(self, step: 'PipelineStep[C, Any]') -> 'PipelineStep[C, Any]':
        """
        Sets the next step in the chain.
        """
        self._next_step = step
        return step

    def should_execute(self, context: C) -> bool:
        """
        Determines if the step should be executed based on the current context.
        """
        return True

    def before(self, context: C) -> None:
        """
        Method executed before the main execution logic.
        """
        pass

    @abstractmethod
    def handle_execution(self, context: C, previous_step_output: I) -> Optional[O]:
        """
        Abstract method containing the core execution logic for the step.
        Must be implemented by concrete pipeline steps.
        It receives the context and the output from the previous step.
        It returns an output object for the next step.
        """
        pass

    def after(self, context: C, output: Optional[O]) -> None:
        """
        Method executed after the main execution logic.
        """
        pass

    def execute(self, context: C, previous_step_output: I = None) -> None:
        """
        Orchestrates the execution of the pipeline step.
        """
        output: Optional[O] = None
        if self.should_execute(context):
            self.before(context)
            output = self.handle_execution(context, previous_step_output)
            self.after(context, output)
        else:
            # If skipped, pass the previous output to the next step
            output = previous_step_output

        context.set_last_executed_step(self)

        if self._next_step:
            self._next_step.execute(context, output)