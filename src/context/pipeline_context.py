from typing import Optional, Any, List
from util.db.execute import SQLExecInfo
from util.db.database_descriptor import DatabaseDescriptor
from pipeline.steps.models.schema_representation import SchemaRepresentation
from pipeline.steps.models.sql_query import SQLQuery

from .generic_context import GenericContext
from executor.task_model import Task
# Import PipelineStep to allow type hinting, but avoid circular dependency
# by using a string literal for the type hint in the class definition.
# from src.pipeline.pipeline_step import PipelineStep


class PipelineContext(GenericContext):
    """
    Context specific to the pipeline, extending GenericContext.
    Stores information relevant to the pipeline execution, including the last executed step.
    """
    def __init__(self, task: Task, db_engine=None, schema_engine=None):
        """
        Initializes the PipelineContext.

        Args:
            db_engine: The database engine.
            schema_engine: The SchemaEngine instance.
            query: The user's natural language query.
            hint: Optional hint or evidence for the query.
        """
        super().__init__(db_engine=db_engine, schema_engine=schema_engine)
        # Add pipeline-specific context attributes here
        self.task = task
        self.user_query = task.question
        self.keywords_and_phrases: dict = None
        self._last_executed_step: Optional[Any] = None # Use Any to avoid circular import issues
        self.preliminary_sql = None
        self.db_schema_per_keyword = {}  # Dictionary to store schema information per keyword
        self.selected_schema: dict = None
        self.selected_schemas: List[dict] = []
        self.hint: Optional[str] = task.evidence
        self.generated_sql_queries: List[SQLQuery] = []
        self.selected_sql_query: Optional[SQLQuery] = None
        self.query_selection_reasoning: Optional[str] = None
        self.query_evaluation_criteria: Optional[str] = None
        self.non_executable_sql_queries: List[SQLQuery] = []
        self.fixed_sql_queries: List[SQLQuery] = []
        self.evaluation_result: Optional[Any] = None
        self.descriptions_database: Optional[DatabaseDescriptor] = None
        self.relevant_entities: dict = {}
        self.unique_table_names: List[str] = []
        self.unique_column_names: List[str] = []
        self.scoring: List[tuple[int, SQLExecInfo]] = []
        self.winning_queries: List[SQLQuery] = []


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
    

    def to_full_dict(self):
        return {
            "user_query": self.user_query,
            "keywords_and_phrases": self.keywords_and_phrases,
            "descriptions_database": self.descriptions_database.to_dict() if self.descriptions_database else None,
            "preliminary_sql": self.preliminary_sql,
            "relevant_entities": self.relevant_entities,
            "db_schema_per_keyword": self.db_schema_per_keyword,
            "selected_schema": self.selected_schema,
            "selected_schemas": [selected_schema for selected_schema in self.selected_schemas],
            "generated_sql_queries": [gen_sql.to_full_dict() for gen_sql in self.generated_sql_queries],
            "non_executable_sql_queries": [query.to_full_dict() for query in self.non_executable_sql_queries],
            "fixed_sql_queries": [query.to_full_dict() for query in self.fixed_sql_queries],
            "scoring": [(score, item.to_dict()) for score, item in self.scoring],
            "selected_sql_query": self.selected_sql_query.to_dict() if self.selected_sql_query else None,
            "query_selection_reasoning": self.query_selection_reasoning,
            "query_evaluation_criteria": self.query_evaluation_criteria,
            "winning_queries": [query.to_full_dict() for query in self.winning_queries]
        }

    def to_dict(self):
        return {
            "user_query": self.user_query,
            "db_schema_per_keyword": self.db_schema_per_keyword,
            "selected_schema": self.selected_schema,
            "generated_sql_queries": [gen_sql.to_dict() for gen_sql in self.generated_sql_queries],
            "non_executable_sql_queries": [query.to_dict() for query in self.non_executable_sql_queries],
            "selected_sql_query": self.selected_sql_query.to_dict() if self.selected_sql_query else None,
            "winning_queries": [query.to_dict() for query in self.winning_queries]
        }
