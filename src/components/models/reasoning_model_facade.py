from .base_model_facade import BaseHuggingFaceFacade
from util.constants import HuggingFaceModelConstants

class ReasoningModelFacade(BaseHuggingFaceFacade):
    """
    Facade for Hugging Face Causal LM models specialized for reasoning tasks.
    """
    def __init__(self, model_name: str = None, model_repo: str = None default_params_override: dict = None):
        effective_model_name = model_name or HuggingFaceModelConstants.DEFAULT_REASONING_MODEL_PATH
        eff_model_repo = model_repo or HuggingFaceModelConstants.DEFAULT_REASONING_MODEL
        super().__init__(model_name=effective_model_name, model_repo = eff_model_repo, default_params_override=default_params_override)

    def _prepare_model_inputs(self, prompt: str, system_prompt: str = None) -> dict:
        """
        Prepares tokenized inputs for reasoning tasks using a system and user prompt.
        """
        messages = []
        effective_system_prompt = system_prompt if system_prompt is not None else "You are a helpful assistant."
        messages.append({"role": "system", "content": effective_system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        templated_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        return self.tokenizer([templated_text], return_tensors="pt").to(self.model.device)

    def _get_task_specific_generation_params(self) -> dict:
        """
        Returns task-specific default generation parameters for reasoning.
        """
        # Example: Reasoning might benefit from slightly different temperature or sampling.
        # These will be layered on top of base defaults and can be overridden by instance or query kwargs.
        return {
            "max_new_tokens": 24000
        }

# if __name__ == '__main__':
#     # Ensure `accelerate` is installed: pip install accelerate
#     # Login to Hugging Face if using gated models: `huggingface-cli login`
#     print("--- ReasoningModelFacade Example Usage ---")
#     try:
#         print("\n[Example: Reasoning Task with ReasoningModelFacade]")
#         # Override default max_new_tokens for this instance
#         reasoning_facade = ReasoningModelFacade(default_params_override={"max_new_tokens": 150})
        
#         reasoning_prompt = "Explain the concept of a facade design pattern in software engineering in simple terms."
#         print(f"Querying '{reasoning_facade.model_name}' for reasoning...")
        
#         # Call-specific override for temperature
#         response_reasoning = reasoning_facade.query(reasoning_prompt, temperature=0.6)
        
#         print(f"\nReasoning Prompt: {reasoning_prompt}")
#         print(f"Reasoning Response:\n{response_reasoning}")

#         # Example with a different system prompt
#         custom_system_prompt = "You are a laconic assistant who provides very short answers."
#         short_prompt = "What is the capital of France?"
#         print(f"\nQuerying '{reasoning_facade.model_name}' with custom system prompt...")
#         response_short = reasoning_facade.query(short_prompt, system_prompt=custom_system_prompt, max_new_tokens=10)
#         print(f"\nShort Prompt: {short_prompt}")
#         print(f"System Prompt: {custom_system_prompt}")
#         print(f"Short Response:\n{response_short}")


#     except Exception as e:
#         print(f"Could not run Reasoning Task example: {e}")
#         print("This might be due to model availability, internet connection, or insufficient resources.")
#         print(f"Make sure the model '{HuggingFaceModelConstants.DEFAULT_REASONING_MODEL}' is accessible.")