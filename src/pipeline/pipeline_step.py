from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any

from context.generic_context import GenericContext
from pipeline.pipeline_step_input import PipelineStepInput

# Define type variables for the generic step
C = TypeVar('C', bound=GenericContext)
I = TypeVar('I', bound=PipelineStepInput)

class PipelineStep(ABC, Generic[C, I]):
    """
    Abstract base class for a step in a pipeline, implementing the
    Chain of Responsibility pattern. Each step processes a context
    and can pass it to the next step in the chain.
    It is generic over the Context type (C) and the Input type (I)
    that the step conceptually uses.
    Includes before, after, handle_execution, and should_execute methods.
    """

    _next_step: Optional['PipelineStep[C, Any]'] = None

    def link_with(self, step: 'PipelineStep[C, Any]') -> 'PipelineStep[C, Any]':
        """
        Sets the next step in the chain.

        Args:
            step: The next PipelineStep instance.

        Returns:
            The next PipelineStep instance, allowing for chaining calls.
        """
        self._next_step = step
        return step

    def should_execute(self, context: C) -> bool:
        """
        Determines if the step should be executed based on the current context.
        Defaults to True. Can be overridden by concrete steps for conditional logic.

        Args:
            context: The current context object.

        Returns:
            True if the step should execute, False otherwise.
        """
        # DEBUG: Checking if step {self.__class__.__name__} should execute.
        return True

    def before(self, context: C) -> None:
        """
        Method executed before the main execution logic.
        Can be overridden by concrete steps for pre-processing.
        Does not return a value.
        """
        # DEBUG: Executing before method for step: {self.__class__.__name__}
        pass

    @abstractmethod
    def handle_execution(self, context: C) -> None:
        """
        Abstract method containing the core execution logic for the step.
        Must be implemented by concrete pipeline steps.
        Modifies the context in place.
        """
        pass

    def after(self, context: C) -> None:
        """
        Method executed after the main execution logic.
        Can be overridden by concrete steps for post-processing or cleanup.
        Does not return a value.
        """
        # DEBUG: Executing after method for step: {self.__class__.__name__}
        pass

    def execute(self, context: C) -> None:
        """
        Orchestrates the execution of the pipeline step,
        calling before, handle_execution, and after methods if should_execute returns True,
        and then delegates to the next step in the chain if one exists.
        Modifies the context in place.
        """
        # INFO: Starting execution check for step: {self.__class__.__name__}
        if self.should_execute(context):
            # INFO: Step {self.__class__.__name__} should execute.
            self.before(context)
            self.handle_execution(context) # handle_execution modifies context in place
            self.after(context)
            # INFO: Finished execution of step: {self.__class__.__name__}
        else:
            # INFO: Step {self.__class__.__name__} skipped execution.
            pass # Skip core logic

        # Update the context with the current step before delegating
        # Assuming the Context class has a method set_last_executed_step
        context.set_last_executed_step(self)

        if self._next_step:
            # DEBUG: Delegating to next step: {self._next_step.__class__.__name__}
            self._next_step.execute(context) # Pass the modified context