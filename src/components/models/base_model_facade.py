import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from abc import ABC, abstractmethod
from util.constants import HuggingFaceModelConstants
import copy

import os
from huggingface_hub import snapshot_download

# Set the environment variable
# Choose HF_HOME or HF_HUB_CACHE based on your preference
os.environ['HF_HUB_CACHE'] = "/var/tmp/ge62nok"
os.environ['HF_HOME'] = "/var/tmp/ge62nok"

model_id = "XGenerationLab/XiYanSQL-QwenCoder-7B-2504"
# Specify your desired local directory
# Make sure this directory has enough disk space and no quota issues!
local_dir = "/tmp/models/XiYanSQL-QwenCoder-7B-2504"
class BaseHuggingFaceFacade(ABC):
    """
    Abstract base class for Hugging Face Causal LM model facades.
    Handles common model loading and querying logic.
    """
    def __init__(self, model_name: str, default_params_override: dict = None):
        # Create the directory if it doesn't exist
        os.makedirs(local_dir, exist_ok=True)

        # Download all files from the model repository
        # If you only need specific files (e.g., just the model weights, not LFS large files if you don't need them),
        # you can use `allow_patterns` or `ignore_patterns`.
        # For a full model, it's usually best to download all.
        model_info = self._get_model_info()
        try:
            snapshot_download(repo_id=model_info["model_name"], local_dir=model_info["path"], local_dir_use_symlinks=False)
            print("Download complete!")
        except Exception as e:
            print(f"Error during download: {e}")
            # You might want to add more specific error handling here, e.g., for disk quota.

        self.model_name = model_name

        # Initialize default generation parameters
        self.default_generation_params = copy.deepcopy(HuggingFaceModelConstants.DEFAULT_MODEL_GENERATION_PARAMS)
        if default_params_override:
            self.default_generation_params.update(default_params_override)

        if not torch.cuda.is_available():
            print(f"Warning: CUDA is not available. Model '{self.model_name}' will run on CPU, which might be very slow.")
            self.device_map_config = None # CPU
        elif torch.cuda.device_count() > 0:
            print(f"{torch.cuda.device_count()} GPU(s) detected. Using device_map='auto' for model '{self.model_name}'.")
            self.device_map_config = "auto"
        else:
             print(f"Warning: CUDA reported available but no devices found. Model '{self.model_name}' will run on CPU.")
             self.device_map_config = None

        try:
            print(f"Loading tokenizer for '{self.model_name}'...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token_id is None:
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
                print(f"Tokenizer pad_token_id set to eos_token_id: {self.tokenizer.eos_token_id}")

            print(f"Loading model '{self.model_name}' with torch_dtype=torch.bfloat16 and device_map='{self.device_map_config or 'cpu'}'...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,
                device_map=self.device_map_config
            )
            print(f"Model '{self.model_name}' loaded successfully.")
            if self.device_map_config == "auto" and hasattr(self.model, 'hf_device_map'):
                 print(f"Model device map: {self.model.hf_device_map}")
            elif hasattr(self.model, 'device'):
                 print(f"Model loaded on device: {self.model.device}")

        except Exception as e:
            print(f"Error loading model '{self.model_name}': {e}")
            raise

    @abstractmethod
    def _prepare_model_inputs(self, prompt: str, system_prompt: str = None) -> dict:
        """
        Prepares the tokenized inputs for the model using appropriate chat templates.
        To be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _get_model_info(self) -> dict:
        """
        Prepares the tokenized inputs for the model using appropriate chat templates.
        To be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _get_task_specific_generation_params(self) -> dict:
        """
        Returns task-specific default generation parameters for the subclass.
        These will be layered on top of the base defaults.
        """
        pass

    def query(self, prompt: str, system_prompt: str = None, **generation_kwargs) -> str | list[str]:
        """
        Sends a prompt to the loaded model and returns the generated text(s).

        Args:
            prompt (str): The input text prompt for the model.
            system_prompt (str, optional): An optional system prompt.
            **generation_kwargs: Call-specific keyword arguments to pass to the model's generate method.
                                 These override all other defaults.

        Returns:
            str | list[str]: The model's generated response(s).
        """
        try:
            model_inputs = self._prepare_model_inputs(prompt, system_prompt)
            
            # Build final generation parameters:
            # 1. Start with a copy of instance's base default parameters
            final_params = copy.deepcopy(self.default_generation_params)
            # 2. Layer task-specific defaults from subclass
            final_params.update(self._get_task_specific_generation_params())
            # 3. Layer call-specific overrides
            final_params.update(generation_kwargs)
            
            # Ensure pad_token_id and eos_token_id are set from tokenizer if not in params
            if "pad_token_id" not in final_params:
                final_params["pad_token_id"] = self.tokenizer.pad_token_id
            if "eos_token_id" not in final_params:
                final_params["eos_token_id"] = self.tokenizer.eos_token_id

            num_return_sequences = final_params.get("num_return_sequences", 1)

            with torch.no_grad():
                generated_ids_full = self.model.generate(
                    **model_inputs,
                    **final_params
                )
            
            input_ids_len = model_inputs["input_ids"].shape[1]
            
            responses = []
            for i in range(num_return_sequences):
                current_sequence_ids = generated_ids_full[i, input_ids_len:]
                response_text = self.tokenizer.decode(current_sequence_ids, skip_special_tokens=True)
                responses.append(response_text.strip())

            return responses if num_return_sequences > 1 else responses[0]

        except Exception as e:
            print(f"Error during model query for '{self.model_name}': {e}")
            if final_params.get("num_return_sequences", 1) > 1:
                return [f"Error generating response: {e}"]
            return f"Error generating response: {e}"