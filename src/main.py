# from infrastructure.database.database_manager import DatabaseManager
# from components.schema.schema_engine_factory import SchemaEngineFactory
# from sqlalchemy.engine import Engine # Import Engine for type hinting

# # Import pipeline components
# from context.pipeline_context import PipelineContext
# from pipeline.pipeline import Pipeline
# from pipeline.noop_pipeline_step import NoOpPipelineStep
import torch
from util.constants import HuggingFaceModelConstants

from components.models.text2sql_model_facade import Text2SQLModelFacade

# if __name__ == "__main__":
#     print("Initializing DatabaseManager...")
#     db_manager = DatabaseManager()

#     database_engine: Engine | None = db_manager._engine # Access the created engine

#     if database_engine:
#         print("Database engine created successfully.")
#         print("Initializing SchemaEngineFactory...")
#         schema_factory = SchemaEngineFactory()

#         print("Creating SchemaEngine instance...")
#         schema_engine = schema_factory.create_schema_engine(engine=database_engine)

#         if schema_engine:
#             print("SchemaEngine instance created successfully.")
#             # TODO: Add further application logic here using schema_engine
#             print(schema_engine.mschema.to_mschema())

#             # --- Pipeline Test ---
#             print("\n--- Testing Pipeline ---")
#             # Create an initial context
#             initial_context = PipelineContext(db_engine=database_engine, schema_engine=schema_engine)

#             # Build the pipeline using the Builder
#             pipeline = Pipeline[PipelineContext].Builder() \
#                 .add_step(NoOpPipelineStep("Step 1")) \
#                 .add_step(NoOpPipelineStep("Step 2")) \
#                 .add_step(NoOpPipelineStep("Step 3")) \
#                 .build()

#             # Run the pipeline
#             pipeline.run(initial_context)

#             print("--- Pipeline Test Finished ---")
#             # --- End Pipeline Test ---


#         else:
#             print("Failed to create SchemaEngine instance.")

#         # Remember to close the database connection when done
#         # db_manager.close_connection() # Consider when/where to close the connection in a real app
#     else:
#         print("Failed to create database engine. Exiting.")


if __name__ == '__main__':
    # Ensure `accelerate` is installed: pip install accelerate
    # Login to Hugging Face if using gated models: `huggingface-cli login`
    print("--- TORCH device count ----", torch.cuda.device_count())

    print("--- Text2SQLModelFacade Example Usage ---")

    # Dummy template for Text2SQL model prompt
    nl2sqlite_template = """\
Instruction: Your task is to convert a natural language question into a SQL query, given a {dialect} database schema.
Schema:
{db_schema}
Question: {question}
Evidence: {evidence}
SQL:
"""
    db_schema_example = """
CREATE TABLE department (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(255) NOT NULL,
    location VARCHAR(255)
);

CREATE TABLE employee (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(255) NOT NULL,
    dept_id INT,
    salary DECIMAL(10, 2),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);
"""
    try:
        print("\n[Example 1: Single SQL Query Generation]")
        # Override default top_p for this instance
        text2sql_facade_single = Text2SQLModelFacade(default_params_override={"top_p": 0.75})
        
        question_1 = "Find the names of all employees in the 'Sales' department."
        prompt_1 = nl2sqlite_template.format(
            dialect="SQLite", db_schema=db_schema_example.strip(), question=question_1, evidence=""
        )
        
        print(f"Querying '{text2sql_facade_single.model_name}' for a single SQL query...")
        # Call-specific override for max_new_tokens
        response_single_sql = text2sql_facade_single.query(prompt_1, max_new_tokens=100)
        
        print(f"\nText2SQL Question: {question_1}")
        print(f"Generated SQL:\n{response_single_sql}")

        print("\n[Example 2: Multiple SQL Query Generation]")
        text2sql_facade_multi = Text2SQLModelFacade() # Uses default Text2SQL model and its params

        question_2 = "What are the names of departments with more than 10 employees?"
        prompt_2 = nl2sqlite_template.format(
            dialect="SQLite", db_schema=db_schema_example.strip(), question=question_2, evidence=""
        )

        num_queries_to_generate = 3
        print(f"Querying '{text2sql_facade_multi.model_name}' for {num_queries_to_generate} SQL queries...")
        
        # Request multiple sequences
        responses_multiple_sql = text2sql_facade_multi.query(prompt_2, num_return_sequences=num_queries_to_generate)
        
        print(f"\nText2SQL Question: {question_2}")
        if isinstance(responses_multiple_sql, list):
            for i, sql in enumerate(responses_multiple_sql):
                print(f"Generated SQL Candidate {i+1}:\n{sql}")
        else: # Should be a list based on num_return_sequences > 1
            print(f"Generated SQL (unexpected single response):\n{responses_multiple_sql}")


    except Exception as e:
        print(f"Could not run Text2SQL Task example: {e}")
        print("This might be due to model availability, internet connection, or insufficient resources.")
        print(f"Make sure the model '{HuggingFaceModelConstants.DEFAULT_TEXT2SQL_MODEL}' is accessible.")