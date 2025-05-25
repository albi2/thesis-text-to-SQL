from sqlalchemy.engine import Engine
from components.schema.schema_engine import SchemaEngine
from typing import Optional

class GenericContext:
    """
    A generic context class to hold common resources.
    """
    def __init__(self, db_engine: Optional[Engine] = None, schema_engine: Optional[SchemaEngine] = None):
        """
        Initializes the GenericContext.

        Args:
            db_engine (Optional[Engine]): The database engine (e.g., SQLAlchemy Engine).
            schema_engine (Optional[SchemaEngine]): The SchemaEngine instance.
        """
        self.db_engine = db_engine
        self.schema_engine = schema_engine

    # You can add other generic resources or methods here