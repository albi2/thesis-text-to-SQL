# Decision Log

This file records architectural and implementation decisions using a list format.
2025-07-04 22:06:00 - Added Query Selection pipeline step.
2025-06-19 23:03:00 - Log of updates made.
2025-06-19 23:28:00 - Refactored pipeline to pass step output as input to the next step.
2025-06-20 15:08:00 - Implemented lazy loading and explicit unloading for models to manage VRAM.
2025-06-20 15:08:00 - Added logic to remove thinking tags from model outputs.

*   **[2025-07-03] SQL Generation Pipeline Step:** Decided to implement a new pipeline step, `SQLGenerationStep`, with a dedicated `SQLGenerationExecutor`, to generate SQL queries based on the filtered schema from the previous step.
*   **[2025-07-03] Asynchronous SQL Execution and Validation:** Decided to implement an asynchronous utility to execute and validate the generated SQL queries. This utility uses `asyncio` to run queries concurrently and returns an `SQLExecInfo` object for each query, containing the query, status, and result.
*   **[2025-07-03] SQL Query Parsing from Model Output:** Decided to implement parsing logic in the `SQLGenerationExecutor` to extract the final SQL query from the model's response, which is expected to be enclosed in `<FINAL_ANSWER>` tags.
*   **[2025-07-04] Query Selection Pipeline Step:** Decided to implement a new pipeline step, `QuerySelectionStep`, with a dedicated `QuerySelectionExecutor`, to select the best SQL query from a list of candidates using a reasoning model.
*

## Decision

*   **[2025-06-20] Lazy Loading and Explicit Unloading of Models:** Decided to implement a lazy loading and explicit unloading mechanism for all Hugging Face and Sentence Transformer models to optimize VRAM usage, especially for GPUs with limited memory.
*   **[2025-06-20] Removal of Thinking Tags from Model Output:** Decided to implement post-processing in the `BaseHuggingFaceFacade` to remove internal "thinking" content (e.g., text within `<think>` tags) from the model's final generated output.
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
*   **[2025-07-04] Query Selection Pipeline Step:** Decided to implement a new pipeline step, `QuerySelectionStep`, with a dedicated `QuerySelectionExecutor`, to select the best SQL query from a list of candidates using a reasoning model.

## Rationale

*   **[2025-05-25] M-Schema Library Integration:** To leverage existing, specialized, and tested code for complex schema handling, aligning with the project's goal of building upon established research and avoiding unnecessary reimplementation.
*   **[2025-05-25] `DatabaseManager` Refactoring for Decoupling:** The original `DatabaseManager` had tight coupling with configuration details and schema engine creation. This refactoring aimed to improve separation of concerns, making the system more modular, testable, and maintainable by centralizing configuration access and schema engine creation logic elsewhere.
*   **[2025-05-25] Use of SQLAlchemy for Database Interaction:** To provide a robust, flexible, and database-agnostic way to manage database connections, execute queries, and potentially handle schema migrations. SQLAlchemy is a mature library that simplifies database operations.
*   **[2025-05-25] Use of PyYAML for Configuration Parsing:** To provide a standard and simple way to load application settings from external YAML files, facilitating easy configuration management.
*   **[2025-05-25] Pipeline Core Structure Design:** To create a modular, extensible, and maintainable way to orchestrate the different stages of the Text-to-SQL process (e.g., schema pruning, query generation, validation). This allows for clear separation of concerns for each processing stage.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** To enable dynamic pipeline behavior where certain steps might be skipped or included based on the current context or the results of previous steps, leading to more adaptive processing.
*   **[2025-06-08] Agent-based Information Retrieval:** To improve modularity by separating the concern of context retrieval from the main Text-to-SQL generation pipeline. This allows for more sophisticated context-aware processing of user queries.
*   **[2025-06-08] Vector Database for Semantic Search:** To improve the accuracy of schema linking by finding relevant tables and columns based on semantic meaning rather than just exact keyword matches. This is crucial for handling diverse and complex natural language queries.
*   **[2025-07-03] SQL Generation Pipeline Step:** To modularize the SQL generation process, separating it from schema filtering and other pipeline steps. This improves maintainability and allows for easier testing and extension of the SQL generation logic.
*   **[2025-07-03] Asynchronous SQL Execution and Validation:** To improve performance by executing multiple generated SQL queries concurrently. This is particularly useful when generating multiple candidate queries, as it allows for faster validation and selection of the best query.
*   **[2025-07-03] SQL Query Parsing from Model Output:** To ensure that only the final, executable SQL query is extracted from the model's potentially verbose output, which may include reasoning or other text. This improves the reliability of the SQL execution step.
*   **[2025-06-08] Dedicated Embedding Model Facade:** To centralize and abstract the process of generating text embeddings, making it easier to manage, update, or swap out the embedding model in the future without affecting other parts of the system.
*   **[2025-06-08] Preprocessing for Vector DB Population:** To ensure that the semantic search capability is fast and efficient at runtime by pre-calculating and indexing all necessary column embeddings.
*   **[2025-06-19] Pipeline Step Output Passing:** This refactoring enhances the clarity and explicitness of data flow between pipeline steps, making the pipeline easier to understand, debug, and extend. It also reduces the reliance on the `PipelineContext` as a central data store for intermediate step results, promoting a more functional approach to pipeline design.
*   **[2025-07-04] Query Selection Pipeline Step:** To improve the accuracy of the final SQL query by using a reasoning model to evaluate multiple candidates based on their relevance and correctness, considering both the query itself and its execution result.

## Rationale

*   **[2025-06-20] Lazy Loading and Explicit Unloading of Models:** To address VRAM limitations on GPUs by ensuring models are only loaded into memory when actively performing a task and are immediately unloaded afterward, preventing multiple large models from residing in VRAM simultaneously.
*   **[2025-06-20] Removal of Thinking Tags from Model Output:** To provide cleaner, more concise model outputs to downstream components or users by stripping internal thought processes that are not part of the final desired response.

## Implementation Details

*   **[2025-06-20] Lazy Loading and Explicit Unloading of Models:**
    *   Modified `BaseHuggingFaceFacade`'s `query` method to call `_load_model_and_tokenizer()` at the start and `unload_model()` in a `finally` block.
    *   Modified `SentenceTransformerEmbeddingFacade`'s `encode` and `encode_single` methods to call `_load_model()` at the start and `unload_model()` in a `finally` block.
    *   Removed explicit `unload_model()` calls from `InformationRetriever` as facades now manage their own lifecycle.
*   **[2025-06-20] Removal of Thinking Tags from Model Output:**
    *   Added logic within `BaseHuggingFaceFacade`'s `query` method to detect and remove content after the `</think>` token (ID 151668) from the generated response.
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
*   **[2025-07-03] SQL Generation Pipeline Step:**
    *   Created `SQLGenerationStep` in [`src/pipeline/steps/sql_generation/sql_generation_step.py`](src/pipeline/steps/sql_generation/sql_generation_step.py) and `SQLGenerationExecutor` in [`src/pipeline/steps/sql_generation/executor/sql_generation_executor.py`](src/pipeline/steps/sql_generation/executor/sql_generation_executor.py).
    *   The executor uses the `Text2SQLModelFacade` to generate SQL queries based on a prompt from [`src/prompts/sql_generation.py`](src/prompts/sql_generation.py).
*   **[2025-07-03] Asynchronous SQL Execution and Validation:**
    *   Created a new utility module [`src/util/db/execute.py`](src/util/db/execute.py) with `execute_sql_queries_async` and `SQLExecInfo` class.
    *   The `SQLGenerationExecutor` uses this utility to execute queries asynchronously and stores the results in the `PipelineContext`.
*   **[2025-07-03] SQL Query Parsing from Model Output:**
    *   Added regex-based parsing in `SQLGenerationExecutor` to extract the SQL query from within `<FINAL_ANSWER>` tags in the model's response.
*   **[2025-05-25] Conditional Step Execution in Pipeline:** Added a `should_execute(context: PipelineContext) -> bool` method to the [`PipelineStep`](src/pipeline/pipeline_step.py:PipelineStep) base class. The pipeline execution logic will check this method before running a step.
*   **[2025-06-08] Agent-based Information Retrieval:** Implemented the [`InformationRetriever`](src/components/agents/information_retriever.py) agent, which uses the [`ReasoningModelFacade`](src/components/models/reasoning_model_facade.py) for keyword extraction and the [`ChromaClient`](src/infrastructure/vector_db/chroma_client.py) for context retrieval.
*   **[2025-06-08] Vector Database for Semantic Search:** Added ChromaDB to [`docker-compose/docker-compose.yaml`](docker-compose/docker-compose.yaml) and implemented a [`ChromaClient`](src/infrastructure/vector_db/chroma_client.py) to interact with it.
*   **[2025-06-08] Dedicated Embedding Model Facade:** Implemented the [`SentenceTransformerEmbeddingFacade`](src/components/models/embedding_model_facade.py) and configured it to use the "Qwen/Qwen2-Embedding-4B" model via [`src/util/constants.py`](src/util/constants.py).
*   **[2025-06-08] Preprocessing for Vector DB Population:** Created the [`populate_column_vectors.py`](scripts/vector_db/populate_column_vectors.py) script to extract schema information using `SchemaEngine` and index it into ChromaDB.
*   **[2025-06-22] Schema Filtering Step Implementation:** Implemented a new pipeline step, `SchemaFilterStep`, with a dedicated `SchemaFilterExecutor`, to refine the database schema context based on information retrieved from the `InformationRetrievalStep` and a reasoning model. This step stores the filtered schema directly in the `PipelineContext`.
*   **[2025-07-04] Query Selection Pipeline Step:**
    *   Created `QuerySelectionStep` in [`src/pipeline/steps/query_selection/query_selection_step.py`](src/pipeline/steps/query_selection/query_selection_step.py) and `QuerySelectionExecutor` in [`src/pipeline/steps/query_selection/executor/query_selection_executor.py`](src/pipeline/steps/query_selection/executor/query_selection_executor.py).
    *   The executor uses the `ReasoningModelFacade` to select the best query based on a prompt from [`src/prompts/query_selection.py`](src/prompts/query_selection.py).
    *   The selected `SQLExecInfo` object is stored in the `selected_sql_query` attribute of the `PipelineContext`.