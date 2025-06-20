# System Patterns

This file documents recurring patterns and standards used in the project.
2025-06-19 23:05:00 - Added Agent and Facade patterns.

*

## Coding Patterns

*   Apply the SOLID principles when organizing code.
*   Each file cannot be more than 750 lines.
*   Code must be well formatted.
*   Classes and functions should follow the single responsibility principle.
*    Keep constant literals in separate classes/files to improve readability and maintainability.
    *   **Example:**
        ```python
        # In src/util/constants.py
        class AppConstants:
            MAX_RETRIES = 3
        # Usage: if attempt < AppConstants.MAX_RETRIES:
        ```
*   Organization of code should be modular and the folder structure should reflect the main components of the application.

## Architectural Patterns

*   **[2025-05-25] Factory Pattern:**
    *   **Guideline:** Use the Factory pattern to create objects when the exact type of object may vary or is determined at runtime. This decouples client code from concrete classes.
    *   **When to use:** For creating families of related objects, or when providing a library of objects and hiding creation complexity.
    *   **Conceptual Example (Method Call):** `service_instance = service_factory.get_service("service_type_A", parameters)`

*   **[2025-05-25] Centralized Configuration Management:**
    *   **Guideline:** Manage application settings by loading them from external configuration files (e.g., YAML, JSON) through a dedicated helper class or module. This centralizes access and allows changes without code modification.
    *   **When to use:** For settings that vary between environments or need user adjustment.
    *   **Conceptual Example (Usage):** `setting_value = config.get("section.key_name")`

*   **[2025-05-25] Chain of Responsibility Pattern:**
    *   **Guideline:** For sequences of processing steps, consider using the Chain of Responsibility pattern. Each handler (step) in the chain decides either to process the request or to pass it to the next handler in the chain. This promotes loose coupling.
    *   **When to use:** When you have multiple objects that can handle a request, and the handler isn't known beforehand, or when you want to decouple senders and receivers of requests.
    *   **Conceptual Example:**
        ```python
        class Handler:
            def set_next(self, handler): # ...
            def handle(self, request): # ...

        # Client code
        handler1 = ConcreteHandlerA()
        handler2 = ConcreteHandlerB()
        handler1.set_next(handler2)
        handler1.handle(some_request)
        ```

*   **[2025-05-25] Builder Pattern:**
    *   **Guideline:** When constructing complex objects with multiple optional parts or configurations, consider using the Builder pattern. It separates the construction of a complex object from its representation, allowing the same construction process to create different representations.
    *   **When to use:** To avoid a constructor with too many parameters, or when you need to create different configurations of an object.
    *   **Conceptual Example:**
        ```python
        class ProductBuilder:
            def set_part_a(self): # ...
            def set_part_b(self): # ...
            def get_result(self): # ...

        # Client code
        builder = ProductBuilder()
        product = builder.set_part_a().set_part_b().get_result()
        ```

*   **[2025-06-08] Facade Pattern:**
    *   **Guideline:** Use a Facade to provide a simplified, unified interface to a more complex subsystem or library. This hides the complexity of the subsystem and decouples it from the client code.
    *   **When to use:** When interacting with external libraries or complex internal components (like different LLM providers or embedding model libraries) to provide a consistent and simple API for the rest of the application.
    *   **Conceptual Example (Usage):** `embeddings = embedding_facade.generate_embeddings(["text1", "text2"])`
    *   **Implementation:** [`SentenceTransformerEmbeddingFacade`](src/components/models/embedding_model_facade.py)

*   **[2025-06-19] Pipeline Step Output Pattern:**
*     **Guideline:** Pipeline steps should explicitly pass their output to the next step in the chain, rather than relying on a shared context object for intermediate results.
*     **When to use:** For designing sequential processing pipelines where the output of one stage directly feeds into the next.
*     **Conceptual Example:**
*         ```python
*         class PipelineStep:
*             def handle_execution(self, context, previous_output) -> current_output:
*                 # process previous_output and context
*                 return current_output
*         ```
*     **Implementation:** [`PipelineStep`](src/pipeline/pipeline_step.py), [`PipelineStepOutput`](src/pipeline/pipeline_step_output.py)

*   **[2025-06-20] Lazy Loading and Explicit Unloading of Models:**
*     **Guideline:** Models (LLMs, embedding models) should be loaded into VRAM only when actively needed for a task and explicitly unloaded immediately after use. This is crucial for managing VRAM on GPUs with limited memory.
*     **When to use:** When multiple large models are used in different parts of the application, but not concurrently, to prevent out-of-memory errors.
*     **Conceptual Example:**
*         ```python
*         class ModelFacade:
*             def process(self, data):
*                 try:
*                     self._load_model()
*                     # Use model to process data
*                     result = self.model.predict(data)
*                     return result
*                 finally:
*                     self.unload_model()
*         ```
*     **Implementation:** [`BaseHuggingFaceFacade`](src/components/models/base_model_facade.py), [`SentenceTransformerEmbeddingFacade`](src/components/models/embedding_model_facade.py)