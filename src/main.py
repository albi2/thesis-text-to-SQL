from infrastructure.database.database_manager import DatabaseManager
from components.schema.schema_engine_factory import SchemaEngineFactory
from sqlalchemy.engine import Engine # Import Engine for type hinting

# Import pipeline components
from pipeline.steps.information_retrieval.executor.information_retriever import InformationRetriever
from context.pipeline_context import PipelineContext
from pipeline.pipeline import Pipeline
from pipeline.steps.information_retrieval.information_retrieval_step import InformationRetrievalStep
from pipeline.steps.print_output.print_output_step import PrintOutputStep
from pipeline.steps.schema_filter.schema_filter_step import SchemaFilterStep
from pipeline.steps.schema_filter.executor.schema_filter_executor import SchemaFilterExecutor
from pipeline.steps.sql_generation.sql_generation_step import SQLGenerationStep
from pipeline.steps.query_selection.query_selection_step import QuerySelectionStep

if __name__ == "__main__":
    print("Initializing DatabaseManager...")
    db_manager = DatabaseManager()

    database_engine: Engine | None = db_manager._engine # Access the created engine

    if database_engine:
        print("Database engine created successfully.")
        print("Initializing SchemaEngineFactory...")
        schema_factory = SchemaEngineFactory()

        print("Creating SchemaEngine instance...")
        schema_engine = schema_factory.create_schema_engine(engine=database_engine)

        if schema_engine:
            print("SchemaEngine instance created successfully.")
            # TODO: Add further application logic here using schema_engine
            print(schema_engine.mschema.to_mschema())

            # --- Pipeline Test ---
            print("\n--- Testing Pipeline ---")
            # Create an initial context
            query = "What are the most common boroughs with the largest offence reports?"
            initial_context = PipelineContext(db_engine=database_engine, schema_engine=schema_engine, query=query)

            # Build the pipeline using the Builder
            pipeline = Pipeline[PipelineContext].Builder() \
                .add_step(InformationRetrievalStep()) \
                .add_step(PrintOutputStep()) \
                .add_step(SchemaFilterStep()) \
                .add_step(PrintOutputStep()) \
                .add_step(SQLGenerationStep()) \
                .add_step(PrintOutputStep()) \
                .add_step(QuerySelectionStep()) \
                .add_step(PrintOutputStep()) \
                .build()

            # Run the pipeline
            pipeline.run(initial_context)

            print("--- Pipeline Test Finished ---")
            # --- End Pipeline Test ---


        else:
            print("Failed to create SchemaEngine instance.")

        # Remember to close the database connection when done
        # db_manager.close_connection() # Consider when/where to close the connection in a real app
    else:
        print("Failed to create database engine. Exiting.")
