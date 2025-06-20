from typing import TypeVar

# Define a type variable for specific output types
O = TypeVar('O', bound='PipelineStepOutput')

class PipelineStepOutput:
    """
    Base class for pipeline step output data structures.
    Specific pipeline steps will define their own output classes
    inheriting from this base class.
    """
    pass