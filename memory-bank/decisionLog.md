# Decision Log

This file records architectural and implementation decisions using a list format.
2025-06-19 23:03:00 - Log of updates made.
2025-06-19 23:28:00 - Refactored pipeline to pass step output as input to the next step.

*

## Decision

*   **[2025-05-25] M-Schema Library Integration:** Decided to integrate components of the M-Schema library for handling database schema representation and processing.
*   **[2025-05-25] `DatabaseManager` Refactoring for Decoupling:** Decided to refactor the `DatabaseManager` to decouple it from direct configuration loading and `SchemaEngine` instantiation, improving modularity.
*   **[2025-05-25] Use of SQLAlchemy for Database Interaction:** Decided to use SQLAlchemy as the ORM and library for database interactions.
*   **[2025-05-25] Use of PyYAML for Configuration Parsing:** Decided to use the PyYAML library for parsing YAML configuration files.
*   **[2025-05-25] Pipeline Core Structure Design:** Decided to implement a core pipeline structure for the Text-to-SQL framework to manage the sequence of operations. This involves defining abstract pipeline steps and a pipeline execution mechanism.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** Decided to incorporate a mechanism for conditional execution of pipeline steps (`should_execute` method) to allow for more flexible and complex workflows.
*   **[2025-06-08] Agent-based Information Retrieval:** Decided to implement an `InformationRetriever` agent to encapsulate the logic for understanding user queries and fetching relevant database schema context.
*   **[2025-06-08] Vector Database for Semantic Search:** Decided to integrate a vector database (ChromaDB) to enable efficient semantic search over database column metadata.
*   **[2025-06-08] Dedicated Embedding Model Facade:** Decided to create a dedicated facade for text embedding models to ensure consistent vector generation and to easily manage the underlying model. Selected "Qwen/Qwen2-Embedding-4B" as the default model.
*   **[2025-06-08] Preprocessing for Vector DB Population:** Decided to create an offline script to populate the vector database with embeddings of database column names and descriptions.
*   **[2025-06-19] Pipeline Step Output Passing:** Decided to refactor the pipeline to pass the output of each step directly as an input to the next step, rather than storing it in the `PipelineContext`.

## Rationale

*   **[2025-05-25] M-Schema Library Integration:** To leverage existing, specialized, and tested code for complex schema handling, aligning with the project's goal of building upon established research and avoiding unnecessary reimplementation.
*   **[2025-05-25] `DatabaseManager` Refactoring for Decoupling:** The original `DatabaseManager` had tight coupling with configuration details and schema engine creation. This refactoring aimed to improve separation of concerns, making the system more modular, testable, and maintainable by centralizing configuration access and schema engine creation logic elsewhere.
*   **[2025-05-25] Use of SQLAlchemy for Database Interaction:** To provide a robust, flexible, and database-agnostic way to manage database connections, execute queries, and potentially handle schema migrations. SQLAlchemy is a mature library that simplifies database operations.
*   **[2025-05-25] Use of PyYAML for Configuration Parsing:** To provide a standard and simple way to load application settings from external YAML files, facilitating easy configuration management.
*   **[2025-05-25] Pipeline Core Structure Design:** To create a modular, extensible, and maintainable way to orchestrate the different stages of the Text-to-SQL process (e.g., schema pruning, query generation, validation). This allows for clear separation of concerns for each processing stage.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** To enable dynamic pipeline behavior where certain steps might be skipped or included based on the current context or the results of previous steps, leading to more adaptive processing.
*   **[2025-06-08] Agent-based Information Retrieval:** To improve modularity by separating the concern of context retrieval from the main Text-to-SQL generation pipeline. This allows for more sophisticated context-aware processing of user queries.
*   **[2025-06-08] Vector Database for Semantic Search:** To improve the accuracy of schema linking by finding relevant tables and columns based on semantic meaning rather than just exact keyword matches. This is crucial for handling diverse and complex natural language queries.
*   **[2025-06-08] Dedicated Embedding Model Facade:** To centralize and abstract the process of generating text embeddings, making it easier to manage, update, or swap out the embedding model in the future without affecting other parts of the system.
*   **[2025-06-08] Preprocessing for Vector DB Population:** To ensure that the semantic search capability is fast and efficient at runtime by pre-calculating and indexing all necessary column embeddings.
*   **[2025-06-19] Pipeline Step Output Passing:** This refactoring enhances the clarity and explicitness of data flow between pipeline steps, making the pipeline easier to understand, debug, and extend. It also reduces the reliance on the `PipelineContext` as a central data store for intermediate step results, promoting a more functional approach to pipeline design.

## Implementation Details

*   **[2025-05-25] M-Schema Library Integration:** Key M-Schema library files (originally `m_schema.py`, `schema_engine.py`, `utils.py`) were adapted and integrated into the project structure, primarily under [`src/components/schema/`](src/components/schema/) and [`src/util/`](src/util/).
*   **[2025-05-25] `DatabaseManager` Refactoring for Decoupling:** The [`DatabaseManager`](src/infrastructure/database/database_manager.py) was modified to utilize the `ConfigurationHelper` (from [`src/common/config/config_manager.py`](src/common/config/config_manager.py)) for accessing configuration settings and the `SchemaEngineFactory` (from [`src/components/schema/schema_engine_factory.py`](src/components/schema/schema_engine_factory.py)) for creating `SchemaEngine` instances.
*   **[2025-05-25] Use of SQLAlchemy for Database Interaction:** SQLAlchemy will be integrated into the [`DatabaseManager`](src/infrastructure/database/database_manager.py) to handle database connection, session management, and query execution.
*   **[2025-05-25] Use of PyYAML for Configuration Parsing:** PyYAML will be used within the [`ConfigurationHelper`](src/common/config/config_manager.py:ConfigurationHelper) in [`src/common/config/config_manager.py`](src/common/config/config_manager.py) to parse [`config/database.yaml`](config/database.yaml) and [`config/schema_engine.yaml`](config/schema_engine.yaml).
*   **[2025-05-25] Pipeline Core Structure Design:** Implemented abstract base class [`PipelineStep`](src/pipeline/pipeline_step.py:PipelineStep) with `before`, `after`, and `handle_execution` methods, and a [`Pipeline`](src/pipeline/pipeline.py:Pipeline) class with a nested `Builder` for constructing the pipeline. The Chain of Responsibility pattern is used for step delegation.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** Added a `should_execute(context: PipelineContext) -> bool` method to the [`PipelineStep`](src/pipeline/pipeline_step.py:PipelineStep) base class. The pipeline execution logic will check this method before running a step.
*   **[2025-06-08] Agent-based Information Retrieval:** Implemented the [`InformationRetriever`](src/components/agents/information_retriever.py) agent, which uses the [`ReasoningModelFacade`](src/components/models/reasoning_model_facade.py) for keyword extraction and the [`ChromaClient`](src/infrastructure/vector_db/chroma_client.py) for context retrieval.
*   **[2025-06-08] Vector Database for Semantic Search:** Added ChromaDB to [`docker-compose/docker-compose.yaml`](docker-compose/docker-compose.yaml) and implemented a [`ChromaClient`](src/infrastructure/vector_db/chroma_client.py) to interact with it.
*   **[2025-06-08] Dedicated Embedding Model Facade:** Implemented the [`SentenceTransformerEmbeddingFacade`](src/components/models/embedding_model_facade.py) and configured it to use the "Qwen/Qwen2-Embedding-4B" model via [`src/util/constants.py`](src/util/constants.py).
*   **[2025-06-08] Preprocessing for Vector DB Population:** Created the [`populate_column_vectors.py`](scripts/vector_db/populate_column_vectors.py) script to extract schema information using `SchemaEngine` and index it into ChromaDB.
*   **[2025-06-19] Pipeline Step Output Passing:**
    *   Modified [`PipelineStep`](src/pipeline/pipeline_step.py) to include `previous_step_output` as a parameter to `handle_execution` and `execute` methods, and to return an output object.
    *   Updated [`Pipeline`](src/pipeline/pipeline.py) to pass the output of one step to the next.
    *   Updated [`InformationRetrievalStep`](src/pipeline/information_retrieval_step.py) to return `InformationRetrievalStepOutput` directly from `handle_execution`.
    *   Removed `step_output` attribute from [`PipelineContext`](src/context/pipeline_context.py).
    *   Created `PipelineStepOutput` as a base class for step outputs.
    *   Created `InformationRetrievalStepOutput` inheriting from `PipelineStepOutput`.

## Implementation Details

*   **[2025-05-25] M-Schema Library Integration:** Key M-Schema library files (originally `m_schema.py`, `schema_engine.py`, `utils.py`) were adapted and integrated into the project structure, primarily under [`src/components/schema/`](src/components/schema/) and [`src/util/`](src/util/).
*   **[2025-05-25] `DatabaseManager` Refactoring for Decoupling:** The [`DatabaseManager`](src/infrastructure/database/database_manager.py) was modified to utilize the `ConfigurationHelper` (from [`src/common/config/config_manager.py`](src/common/config/config_manager.py)) for accessing configuration settings and the `SchemaEngineFactory` (from [`src/components/schema/schema_engine_factory.py`](src/components/schema/schema_engine_factory.py)) for creating `SchemaEngine` instances.
*   **[2025-05-25] Use of SQLAlchemy for Database Interaction:** SQLAlchemy will be integrated into the [`DatabaseManager`](src/infrastructure/database/database_manager.py) to handle database connection, session management, and query execution.
*   **[2025-05-25] Use of PyYAML for Configuration Parsing:** PyYAML will be used within the [`ConfigurationHelper`](src/common/config/config_manager.py:ConfigurationHelper) in [`src/common/config/config_manager.py`](src/common/config/config_manager.py) to parse [`config/database.yaml`](config/database.yaml) and [`config/schema_engine.yaml`](config/schema_engine.yaml).
*   **[2025-05-25] Pipeline Core Structure Design:** Implemented abstract base class [`PipelineStep`](src/pipeline/pipeline_step.py:PipelineStep) with `before`, `after`, and `handle_execution` methods, and a [`Pipeline`](src/pipeline/pipeline.py:Pipeline) class with a nested `Builder` for constructing the pipeline. The Chain of Responsibility pattern is used for step delegation.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** Added a `should_execute(context: PipelineContext) -> bool` method to the [`PipelineStep`](src/pipeline/pipeline_step.py:PipelineStep) base class. The pipeline execution logic will check this method before running a step.
*   **[2025-06-08] Agent-based Information Retrieval:** Implemented the [`InformationRetriever`](src/components/agents/information_retriever.py) agent, which uses the [`ReasoningModelFacade`](src/components/models/reasoning_model_facade.py) for keyword extraction and the [`ChromaClient`](src/infrastructure/vector_db/chroma_client.py) for context retrieval.
*   **[2025-06-08] Vector Database for Semantic Search:** Added ChromaDB to [`docker-compose/docker-compose.yaml`](docker-compose/docker-compose.yaml) and implemented a [`ChromaClient`](src/infrastructure/vector_db/chroma_client.py) to interact with it.
*   **[2025-06-08] Dedicated Embedding Model Facade:** Implemented the [`SentenceTransformerEmbeddingFacade`](src/components/models/embedding_model_facade.py) and configured it to use the "Qwen/Qwen2-Embedding-4B" model via [`src/util/constants.py`](src/util/constants.py).
*   **[2025-06-08] Preprocessing for Vector DB Population:** Created the [`populate_column_vectors.py`](scripts/vector_db/populate_column_vectors.py) script to extract schema information using `SchemaEngine` and index it into ChromaDB.