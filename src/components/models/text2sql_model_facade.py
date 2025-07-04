from .base_model_facade import BaseHuggingFaceFacade
from util.constants import HuggingFaceModelConstants

class Text2SQLModelFacade(BaseHuggingFaceFacade):
    """
    Facade for Hugging Face Causal LM models specialized for Text-to-SQL tasks.
    Supports generating multiple SQL query candidates.
    """
    def __init__(self, model_name: str = None, model_repo: str = None, default_params_override: dict = None):
        eff_model_name = model_name or HuggingFaceModelConstants.DEFAULT_TEXT2SQL_MODEL_PATH
        eff_model_repo = model_repo or HuggingFaceModelConstants.DEFAULT_TEXT2SQL_MODEL
        super().__init__(model_name=eff_model_name, model_repo = eff_model_repo, default_params_override=default_params_override)

    def _prepare_model_inputs(self, prompt: str, system_prompt: str = None) -> dict:
        """
        Prepares tokenized inputs for Text2SQL tasks.
        The prompt is expected to be fully formatted. System prompt is usually not separate.
        """
        if system_prompt:
            print("Warning: System prompt provided to Text2SQLModelFacade. "
                  "Ensure your main prompt includes all necessary instructions, "
                  "as system prompts are typically not used separately in the chat template for Text2SQL.")

        messages = [{"role": "user", "content": prompt}]
        
        templated_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        return self.tokenizer([templated_text], return_tensors="pt").to(self.model.device)

    def _get_task_specific_generation_params(self) -> dict:
        """
        Returns task-specific default generation parameters for Text2SQL.
        """
        return {
            # "temperature": 0.1,
            # "do_sample": True,
            # "top_p": 0.8, 
            "max_new_tokens": 1024
            # top_p is already handled by base defaults or instance override
        }

    def query(self, prompt: str, system_prompt: str = None, **generation_kwargs) -> str | list[str]:
        """
        Sends a prompt to the loaded Text2SQL model and returns the generated SQL query(s).

        Args:
            prompt (str): The fully formatted input text prompt for the Text2SQL model.
            system_prompt (str, optional): Typically not used for Text2SQL; instructions
                                           should be in the main prompt.
            num_return_sequences (int): The number of SQL queries to generate.
                                        Defaults to 1.
            **generation_kwargs: Additional keyword arguments to pass to the model's generate method.
                                 Overrides defaults.

        Returns:
            str | list[str]: A single SQL query string if num_return_sequences is 1,
                             otherwise a list of SQL query strings.
        """
        # Pass num_return_sequences to the base class query method via generation_kwargs


        return super().query(prompt, system_prompt=system_prompt, **generation_kwargs)
        

# if __name__ == '__main__':
#     # Ensure `accelerate` is installed: pip install accelerate
#     # Login to Hugging Face if using gated models: `huggingface-cli login`
#     print("--- Text2SQLModelFacade Example Usage ---")

#     # Dummy template for Text2SQL model prompt
#     nl2sqlite_template = """\
# Instruction: Your task is to convert a natural language question into a SQL query, given a {dialect} database schema.
# Schema:
# {db_schema}
# Question: {question}
# Evidence: {evidence}
# SQL:
# """
#     db_schema_example = """
# CREATE TABLE department (
#     dept_id INT PRIMARY KEY,
#     dept_name VARCHAR(255) NOT NULL,
#     location VARCHAR(255)
# );

# CREATE TABLE employee (
#     emp_id INT PRIMARY KEY,
#     emp_name VARCHAR(255) NOT NULL,
#     dept_id INT,
#     salary DECIMAL(10, 2),
#     FOREIGN KEY (dept_id) REFERENCES department(dept_id)
# );
# """
#     try:
#         print("\n[Example 1: Single SQL Query Generation]")
#         # Override default top_p for this instance
#         text2sql_facade_single = Text2SQLModelFacade(default_params_override={"top_p": 0.75})
        
#         question_1 = "Find the names of all employees in the 'Sales' department."
#         prompt_1 = nl2sqlite_template.format(
#             dialect="SQLite", db_schema=db_schema_example.strip(), question=question_1, evidence=""
#         )
        
#         print(f"Querying '{text2sql_facade_single.model_name}' for a single SQL query...")
#         # Call-specific override for max_new_tokens
#         response_single_sql = text2sql_facade_single.query(prompt_1, max_new_tokens=100)
        
#         print(f"\nText2SQL Question: {question_1}")
#         print(f"Generated SQL:\n{response_single_sql}")

#         print("\n[Example 2: Multiple SQL Query Generation]")
#         text2sql_facade_multi = Text2SQLModelFacade() # Uses default Text2SQL model and its params

#         question_2 = "What are the names of departments with more than 10 employees?"
#         prompt_2 = nl2sqlite_template.format(
#             dialect="SQLite", db_schema=db_schema_example.strip(), question=question_2, evidence=""
#         )

#         num_queries_to_generate = 3
#         print(f"Querying '{text2sql_facade_multi.model_name}' for {num_queries_to_generate} SQL queries...")
        
#         # Request multiple sequences
#         responses_multiple_sql = text2sql_facade_multi.query(prompt_2, num_return_sequences=num_queries_to_generate)
        
#         print(f"\nText2SQL Question: {question_2}")
#         if isinstance(responses_multiple_sql, list):
#             for i, sql in enumerate(responses_multiple_sql):
#                 print(f"Generated SQL Candidate {i+1}:\n{sql}")
#         else: # Should be a list based on num_return_sequences > 1
#             print(f"Generated SQL (unexpected single response):\n{responses_multiple_sql}")

#     except Exception as e:
#         print(f"Could not run Text2SQL Task example: {e}")
#         print("This might be due to model availability, internet connection, or insufficient resources.")
#         print(f"Make sure the model '{HuggingFaceModelConstants.DEFAULT_TEXT2SQL_MODEL}' is accessible.")