# Lessons Learned - Database and Schema Engine

## Schema Engine Refactoring

**Problem:** The initial implementation of the schema engine and M-SQL schema classes had tightly coupled responsibilities, making them difficult to maintain and extend.

**Solution:**
- Applied the single responsibility principle to separate concerns.
- Introduced a `schema_engine_factory.py` to handle the creation of different schema engine types based on configuration, decoupling the main logic from specific implementations.
- Broke down the `m_schema.py` and `schema_engine.py` files into smaller, more focused functions and classes.

## Configuration Management

**Problem:** Hardcoding database connection details and schema engine settings made the application inflexible and difficult to configure for different environments.

**Solution:**
- Implemented a centralized configuration manager (`config_manager.py`) to load settings from external YAML files (`config/database.yaml`, `config/schema_engine.yaml`).
- This allows easy modification of settings without requiring code changes and improves maintainability.

## Tools and Libraries

- **PyYAML**: Used for parsing YAML configuration files, providing a simple way to manage application settings externally.
- **SQLAlchemy**: (Implied from database connection) Used for database interaction, providing an ORM and a flexible way to connect to different database types.

## Edge Cases

- Handling of invalid or missing configuration values: The `config_manager.py` should include validation or default values to prevent errors when configuration files are incomplete or incorrect.
- Ensuring compatibility with different database drivers: The `database_manager.py` needs to be robust enough to handle various database backends supported by SQLAlchemy.