from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from components.schema.schema_engine import SchemaEngine
from common.config.config_helper import ConfigurationHelper
from util.constants import DatabaseConfigKeys, DatabaseConstants # Import DatabaseConstants

class DatabaseManager:
    def __init__(self):
        """
        Initializes the DatabaseManager and establishes a database connection.
        Configuration is loaded using ConfigurationHelper.
        """
        config_helper = ConfigurationHelper()
        # Load the 'database' section from 'database.yaml'
        self.config = config_helper.get_config("database.yaml", "database")

        self._engine = None
        self._connection = None

        if not self.config:
            print("Failed to load database configuration. Cannot proceed.")
        else:
            self._ensure_database_exists() # Ensure database exists before creating engine
            self._engine = self._create_engine()
            if self._engine:
                 self._connection = self._connect()


    def _ensure_database_exists(self):
        """Ensures the target database exists, creating it if configured to do so."""
        create_db_flag = self.config.get(DatabaseConfigKeys.CREATE_DATABASE_IF_NOT_EXISTS, False)
        db_name = self.config.get(DatabaseConfigKeys.DATABASE_NAME)
        host = self.config.get(DatabaseConfigKeys.HOST)
        port = self.config.get(DatabaseConfigKeys.PORT)
        user = self.config.get(DatabaseConfigKeys.USERNAME)
        password = self.config.get(DatabaseConfigKeys.PASSWORD)

        if not all([db_name, host, port, user, password]):
            print("Missing database connection details in configuration. Cannot ensure database exists.")
            return

        if create_db_flag:
            # Attempt to connect to the default 'postgres' database to create the target database
            # Use a temporary engine for the default database
            default_db_url = DatabaseConstants.DEFAULT_DB_URL_FORMAT.format(
                user=user,
                password=password,
                host=host,
                port=port,
                database=DatabaseConstants.DEFAULT_DB_NAME # Use the default database name constant
            )
            engine_default = None # Initialize engine_default to None
            try:
                engine_default = create_engine(default_db_url)
                with engine_default.connect() as connection:
                    # Check if database exists using the constant
                    result = connection.execute(text(DatabaseConstants.CHECK_DB_EXISTS_SQL), {"db_name": db_name})
                    exists = result.fetchone()

                    if not exists:
                        print(f"Database '{db_name}' does not exist. Creating...")
                        # Disconnect all other connections to the database before dropping/creating
                        # This is often necessary in PostgreSQL
                        try:
                            connection.execute(text(DatabaseConstants.TERMINATE_DB_CONNECTIONS_SQL), {"db_name": db_name})
                        except ProgrammingError:
                             # Database might not exist yet, so terminating connections might fail, which is fine.
                             pass
                        # Create the database using the constant
                        connection.execute(text(DatabaseConstants.CREATE_DATABASE_SQL), {"db_name": db_name})
                        print(f"Database '{db_name}' created.")
                    else:
                        print(f"Database '{db_name}' already exists.")
            except OperationalError as e:
                print(f"Error ensuring database '{db_name}' exists: {e}")
                print("Please ensure the PostgreSQL server is running and accessible.")
            except Exception as e:
                print(f"An unexpected error occurred while ensuring database exists: {e}")
            finally:
                 # Dispose the temporary engine
                 if engine_default: 
                    engine_default.dispose()


    def _create_engine(self):
        """Creates the SQLAlchemy engine for the target database."""
        host = self.config.get(DatabaseConfigKeys.HOST)
        port = self.config.get(DatabaseConfigKeys.PORT)
        user = self.config.get(DatabaseConfigKeys.USERNAME)
        password = self.config.get(DatabaseConfigKeys.PASSWORD)
        database_name = self.config.get(DatabaseConfigKeys.DATABASE_NAME)

        if not all([host, port, user, password, database_name]):
            print("Missing database connection details in configuration. Cannot create engine.")
            return None

        # Construct the database URL using the constant format string
        database_url = DatabaseConstants.DEFAULT_DB_URL_FORMAT.format(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database_name
        )

        try:
            engine = create_engine(database_url)
            # Optional: Test the connection
            # with engine.connect() as connection:
            #     connection.execute(text("SELECT 1"))
            print(f"SQLAlchemy engine created for database '{database_name}'.")
            return engine
        except Exception as e:
            print(f"Error creating SQLAlchemy engine for database '{database_name}': {e}")
            return None

    def _connect(self):
        """Establishes a connection from the engine."""
        if not self._engine:
            print("Cannot establish connection: SQLAlchemy engine not created.")
            return None
        try:
            connection = self._engine.connect()
            print("Database connection established via SQLAlchemy engine.")
            return connection
        except OperationalError as e:
             print(f"Error establishing connection via SQLAlchemy engine: {e}")
             print("Please ensure the database is accessible.")
             return None
        except Exception as e:
            print(f"An unexpected error occurred during connection establishment: {e}")
            return None


    # Removed get_schema_engine as requested

    def close_connection(self):
        """Closes the database connection and disposes the engine."""
        if self._connection:
            try:
                self._connection.close()
                print("Database connection closed.")
            except Exception as e:
                print(f"Error closing database connection: {e}")
            self._connection = None

        if self._engine:
            try:
                self._engine.dispose()
                print("SQLAlchemy engine disposed.")
            except Exception as e:
                print(f"Error disposing SQLAlchemy engine: {e}")
            self._engine = None

# Example Usage (optional, for testing)
# if __name__ == "__main__":
#     # Ensure you have a config/database.yaml and a running PostgreSQL container
#     # with database: govukdata, user: admin, password: admin
#     db_manager = DatabaseManager()
#     # The connection is established during initialization if config is valid and db exists/created
#     if db_manager._connection:
#         # Removed get_schema_engine call
#         # Example of executing a query (requires an active connection)
#         # try:
#         #     result = db_manager._connection.execute(text("SELECT 1"))
#         #     print("Test query result:", result.fetchone())
#         # except Exception as e:
#         #     print(f"Error executing test query: {e}")
#         db_manager.close_connection()
#     else:
#         print("Failed to initialize DatabaseManager or connect to database.")