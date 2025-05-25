class DatabaseConfigKeys:
    """
    Constants for database configuration keys.
    """
    HOST = "host"
    PORT = "port"
    USERNAME = "username"
    PASSWORD = "password"
    DATABASE_NAME = "database_name"
    CREATE_DATABASE_IF_NOT_EXISTS = "create_database_if_not_exists"
    # Add other database config keys here as needed
    # POOL_SIZE = "pool_size"
    # TIMEOUT = "timeout"

class DatabaseConstants:
    """
    General database-related constants.
    """
    DEFAULT_DB_NAME = "govdata"

    # SQL Queries with named placeholders for SQLAlchemy text()
    CHECK_DB_EXISTS_SQL = "SELECT 1 FROM pg_database WHERE datname = :db_name"
    CREATE_DATABASE_SQL = "CREATE DATABASE :db_name"
    TERMINATE_DB_CONNECTIONS_SQL = "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = :db_name AND pid <> pg_backend_pid();"

    # Default database URL format string
    DEFAULT_DB_URL_FORMAT = "postgresql://{user}:{password}@{host}:{port}/{database}"