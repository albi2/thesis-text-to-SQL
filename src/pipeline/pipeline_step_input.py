from typing import TypeVar, Generic

# Define a type variable for specific input types
I = TypeVar('I', bound='PipelineStepInput')

class PipelineStepInput:
    """
    Base class for pipeline step input data structures.
    Specific pipeline steps will define their own input classes
    inheriting from this base class.
    """
    pass