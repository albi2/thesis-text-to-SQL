# Decision Log

This file records architectural and implementation decisions using a list format.
2025-05-31 02:11:44 - Log of updates made.

*

## Decision

*   **[2025-05-25] M-Schema Library Integration:** Decided to integrate components of the M-Schema library for handling database schema representation and processing.
*   **[2025-05-25] `DatabaseManager` Refactoring for Decoupling:** Decided to refactor the `DatabaseManager` to decouple it from direct configuration loading and `SchemaEngine` instantiation, improving modularity.
*   **[2025-05-25] Use of SQLAlchemy for Database Interaction:** Decided to use SQLAlchemy as the ORM and library for database interactions.
*   **[2025-05-25] Use of PyYAML for Configuration Parsing:** Decided to use the PyYAML library for parsing YAML configuration files.
*   **[2025-05-25] Pipeline Core Structure Design:** Decided to implement a core pipeline structure for the Text-to-SQL framework to manage the sequence of operations. This involves defining abstract pipeline steps and a pipeline execution mechanism.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** Decided to incorporate a mechanism for conditional execution of pipeline steps (`should_execute` method) to allow for more flexible and complex workflows.

## Rationale

*   **[2025-05-25] M-Schema Library Integration:** To leverage existing, specialized, and tested code for complex schema handling, aligning with the project's goal of building upon established research and avoiding unnecessary reimplementation.
*   **[2025-05-25] `DatabaseManager` Refactoring for Decoupling:** The original `DatabaseManager` had tight coupling with configuration details and schema engine creation. This refactoring aimed to improve separation of concerns, making the system more modular, testable, and maintainable by centralizing configuration access and schema engine creation logic elsewhere.
*   **[2025-05-25] Use of SQLAlchemy for Database Interaction:** To provide a robust, flexible, and database-agnostic way to manage database connections, execute queries, and potentially handle schema migrations. SQLAlchemy is a mature library that simplifies database operations.
*   **[2025-05-25] Use of PyYAML for Configuration Parsing:** To provide a standard and simple way to load application settings from external YAML files, facilitating easy configuration management.
*   **[2025-05-25] Pipeline Core Structure Design:** To create a modular, extensible, and maintainable way to orchestrate the different stages of the Text-to-SQL process (e.g., schema pruning, query generation, validation). This allows for clear separation of concerns for each processing stage.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** To enable dynamic pipeline behavior where certain steps might be skipped or included based on the current context or the results of previous steps, leading to more adaptive processing.

## Implementation Details

*   **[2025-05-25] M-Schema Library Integration:** Key M-Schema library files (originally `m_schema.py`, `schema_engine.py`, `utils.py`) were adapted and integrated into the project structure, primarily under [`src/components/schema/`](src/components/schema/) and [`src/util/`](src/util/).
*   **[2025-05-25] `DatabaseManager` Refactoring for Decoupling:** The [`DatabaseManager`](src/infrastructure/database/database_manager.py) was modified to utilize the `ConfigurationHelper` (from [`src/common/config/config_manager.py`](src/common/config/config_manager.py)) for accessing configuration settings and the `SchemaEngineFactory` (from [`src/components/schema/schema_engine_factory.py`](src/components/schema/schema_engine_factory.py)) for creating `SchemaEngine` instances.
*   **[2025-05-25] Use of SQLAlchemy for Database Interaction:** SQLAlchemy will be integrated into the [`DatabaseManager`](src/infrastructure/database/database_manager.py) to handle database connection, session management, and query execution.
*   **[2025-05-25] Use of PyYAML for Configuration Parsing:** PyYAML will be used within the [`ConfigurationHelper`](src/common/config/config_manager.py:ConfigurationHelper) in [`src/common/config/config_manager.py`](src/common/config/config_manager.py) to parse [`config/database.yaml`](config/database.yaml) and [`config/schema_engine.yaml`](config/schema_engine.yaml).
*   **[2025-05-25] Pipeline Core Structure Design:** Implemented abstract base class [`PipelineStep`](src/pipeline/pipeline_step.py:PipelineStep) with `before`, `after`, and `handle_execution` methods, and a [`Pipeline`](src/pipeline/pipeline.py:Pipeline) class with a nested `Builder` for constructing the pipeline. The Chain of Responsibility pattern is used for step delegation.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** Added a `should_execute(context: PipelineContext) -> bool` method to the [`PipelineStep`](src/pipeline/pipeline_step.py:PipelineStep) base class. The pipeline execution logic will check this method before running a step.