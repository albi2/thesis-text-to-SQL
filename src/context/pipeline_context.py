from typing import Optional, Any, List
from util.db.execute import SQLExecInfo # Import locally to avoid circular dependency

from .generic_context import GenericContext
# Import PipelineStep to allow type hinting, but avoid circular dependency
# by using a string literal for the type hint in the class definition.
# from src.pipeline.pipeline_step import PipelineStep


class PipelineContext(GenericContext):
    """
    Context specific to the pipeline, extending GenericContext.
    Stores information relevant to the pipeline execution, including the last executed step.
    """
    def __init__(self, db_engine=None, schema_engine=None, query = None):
        """
        Initializes the PipelineContext.

        Args:
            db_engine: The database engine.
            schema_engine: The SchemaEngine instance.
        """
        super().__init__(db_engine=db_engine, schema_engine=schema_engine)
        # Add pipeline-specific context attributes here
        self.user_query = query
        self._last_executed_step: Optional[Any] = None # Use Any to avoid circular import issues
        self.db_schema_per_keyword = {}  # Dictionary to store schema information per keyword
        self.selected_schema: dict = None
        self.hint: Optional[str] = None
        self.generated_sql_queries: List[SQLExecInfo] = []


    def set_last_executed_step(self, step: Any) -> None: # Use Any for type hint
        """
        Sets the last executed pipeline step in the context.

        Args:
            step: The PipelineStep instance that was just executed.
        """
        self._last_executed_step = step

    def get_last_executed_step(self) -> Optional[Any]: # Use Any for return type
        """
        Gets the last executed pipeline step from the context.

        Returns:
            The last executed PipelineStep instance, or None if no step has been executed yet.
        """
        return self._last_executed_step

    def to_dict(self):
        return {
            "user_query": self.user_query,
            "db_schema_per_keyword": self.db_schema_per_keyword,
            "selected_schema": self.selected_schema
        }