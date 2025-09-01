from sqlalchemy.engine import Engine
from components.schema.schema_engine import SchemaEngine
from common.config.config_helper import ConfigurationHelper

class SchemaEngineFactory:
    """
    Factory for creating SchemaEngine instances based on configuration.
    """
    def __init__(self):
        self._config_helper = ConfigurationHelper()

    def create_schema_engine(self, engine: Engine, db_name: str) -> SchemaEngine:
        """
        Creates a SchemaEngine instance using configuration from schema_engine.yaml.

        Args:
            engine (Engine): The SQLAlchemy engine to use for the SchemaEngine.

        Returns:
            SchemaEngine: An instance of SchemaEngine.
        """
        # Load the 'schema_engine' section from 'schema_engine.yaml'
        schema_engine_config = self._config_helper.get_config("schema_engine.yaml", "schema_engine")

        if not schema_engine_config:
            print("Failed to load SchemaEngine configuration. Using default parameters.")
            # Return SchemaEngine with only the required engine parameter
            return SchemaEngine(engine=engine)

        # Extract parameters from the loaded configuration
        schema = schema_engine_config.get("schema")
        ignore_tables = schema_engine_config.get("ignore_tables")
        include_tables = schema_engine_config.get("include_tables")
        sample_rows_in_table_info = schema_engine_config.get("sample_rows_in_table_info", 3)
        indexes_in_table_info = schema_engine_config.get("indexes_in_table_info", False)
        custom_table_info = schema_engine_config.get("custom_table_info", {})
        view_support = schema_engine_config.get("view_support", False)
        max_string_length = schema_engine_config.get("max_string_length", 300)

        # Instantiate SchemaEngine with configured parameters
        return SchemaEngine(
            engine=engine,
            # schema=schema,
            ignore_tables=ignore_tables,
            include_tables=include_tables,
            sample_rows_in_table_info=sample_rows_in_table_info,
            indexes_in_table_info=indexes_in_table_info,
            custom_table_info=custom_table_info,
            view_support=view_support,
            max_string_length=max_string_length,
            db_name=db_name 
            # mschema is handled internally by SchemaEngine if not provided
        )

# Example Usage (optional, for testing)
# if __name__ == "__main__":
#     # This example requires a running database and a valid config/database.yaml
#     # and config/schema_engine.yaml
#     from src.infrastructure.database.database_manager import DatabaseManager
#
#     db_manager = DatabaseManager()
#     if db_manager._engine:
#         schema_factory = SchemaEngineFactory()
#         schema_engine = schema_factory.create_schema_engine(db_manager._engine)
#         print(f"SchemaEngine instance created by factory: {schema_engine}")
#         # You can now use schema_engine methods, e.g., schema_engine.get_usable_tables()
#         db_manager.close_connection()
#     else:
#         print("Failed to initialize DatabaseManager or get engine.")