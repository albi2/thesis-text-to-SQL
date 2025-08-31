import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True,max_split_size_mb:128'
os.environ['PYTORCH_NVML_BASED_CUDA_CHECK'] = "1"

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from abc import ABC, abstractmethod
from util.constants import HuggingFaceModelConstants
import copy

import gc
from huggingface_hub import snapshot_download
# Set the environment variable
# Choose HF_HOME or HF_HUB_CACHE based on your preference
os.environ['HF_HUB_CACHE'] = "/workspace/data"
os.environ['HF_HOME'] = "/workspace/data"
os.environ['PYTORCH_NVML_BASED_CUDA_CHECK'] = "1"

class BaseHuggingFaceFacade(ABC):
    """
    Abstract base class for Hugging Face Causal LM model facades.
    Handles common model loading and querying logic with lazy loading.
    """
    def __init__(self, model_name: str, model_repo: str, default_params_override: dict = None):
        self.model_name = model_name
        self.model_repo = model_repo
        self._model = None
        self._tokenizer = None
        self.device_map_config = None

        # Initialize default generation parameters
        self.default_generation_params = copy.deepcopy(HuggingFaceModelConstants.DEFAULT_MODEL_GENERATION_PARAMS)
        if default_params_override:
            self.default_generation_params.update(default_params_override)

        # Download the model files in the constructor
        self._download_model_files()

    def _download_model_files(self):
        """Downloads model files from Hugging Face Hub."""
        local_path = self.model_name
        repo_id = self.model_repo

        if not local_path or not repo_id:
            print(f"Warning: Model info for '{self.model_name}' is incomplete. Skipping download.")
            return
            
        try:
            print(f"Ensuring model '{repo_id}' is downloaded to '{local_path}'...")
            os.makedirs(local_path, exist_ok=True)
            snapshot_download(repo_id=repo_id, local_dir=local_path)
            print(f"Download/verification complete for '{repo_id}'.")
        except Exception as e:
            print(f"Error during download for '{repo_id}': {e}")
            # The loading might still succeed if the model is cached, so we don't raise here.
            pass

    @property
    def model(self):
        """Property to access the model, triggers loading on first access."""
        if self._model is None:
            self._load_model_and_tokenizer()
        return self._model

    @property
    def tokenizer(self):
        """Property to access the tokenizer, triggers loading on first access."""
        if self._tokenizer is None:
            self._load_model_and_tokenizer()
        return self._tokenizer

    def _load_model_and_tokenizer(self):
        """Loads the model and tokenizer on demand."""
        if self._model is not None and self._tokenizer is not None:
            return

        print(f"--- Starting lazy load for: {self.model_name} ---")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i} allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
            print(f"GPU {i} reserved: {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")

        # Determine device mapping
        if not torch.cuda.is_available():
            # print(f"Warning: CUDA not available. Model '{self.model_name}' will run on CPU.")
            # self.device_map_config = None
            raise RuntimeError("No GPU found! Please make sure a CUDA-enabled GPU is available.")
        else:
            print(f"{torch.cuda.device_count()} GPU(s) detected. Using device_map='auto' for '{self.model_name}'.")
            self.device_map_config = "auto"
        
        # self.device_map_config = "auto"
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i} allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
            print(f"GPU {i} reserved: {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")

        try:
            print(f"Loading tokenizer for '{self.model_name}'...")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self._tokenizer.pad_token_id is None:
                self._tokenizer.pad_token_id = self._tokenizer.eos_token_id
                print(f"Tokenizer pad_token_id set to eos_token_id: {self._tokenizer.eos_token_id}")

            print(f"Loading model '{self.model_name}' with torch_dtype=torch.bfloat16 and device_map='{self.device_map_config or 'cpu'}'...")
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,
                device_map=self.device_map_config
            )
            # self._model = self._model.to_bettertransformer()
            print(f"Model '{self.model_name}' loaded successfully.")
            if self.device_map_config == "auto" and hasattr(self._model, 'hf_device_map'):
                 print(f"Model device map: {self._model.hf_device_map}")
            elif hasattr(self._model, 'device'):
                 print(f"Model loaded on device: {self._model.device}")

        except Exception as e:
            print(f"Error loading model '{self.model_name}': {e}")
            self._model = None
            self._tokenizer = None
            raise
        print(f"--- Finished lazy load for: {self.model_name} ---")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i} allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
            print(f"GPU {i} reserved: {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")

    def unload_model(self):
        """Unloads the model and tokenizer to free up memory."""
        if self._model is None and self._tokenizer is None:
            print(f"Model '{self.model_name}' is not loaded, nothing to unload.")
            return

        print(f"Unloading model and tokenizer for '{self.model_name}'...")
        del self._model
        del self._tokenizer
        self._model = None
        self._tokenizer = None
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                torch.cuda.set_device(i)
                # torch.cuda.empty_cache() 
                # torch.cuda.ipc_collect()
                # torch.cuda.synchronize()
                torch.cuda.empty_cache()
                gc.collect()
        
        # if hasattr(torch.cuda, 'memory'):
        #     for i in range(torch.cuda.device_count()):
        #         torch.cuda.set_device(i)
        #         # This forces the allocator to release unused blocks
        #         torch.cuda.memory.empty_cache()


        for i in range(torch.cuda.device_count()):
            torch.cuda.memory._dump_snapshot()  # Debug info
            torch.cuda.reset_accumulated_memory_stats(i)
            torch.cuda.reset_peak_memory_stats(i)
        print(f"Model '{self.model_name}' unloaded successfully.")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i} allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
            print(f"GPU {i} reserved: {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")

    @abstractmethod
    def _prepare_model_inputs(self, prompt: str, system_prompt: str = None) -> dict:
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
        The model and tokenizer are loaded at the beginning of this method and
        unloaded at the end to manage VRAM.

        Args:
            prompt (str): The input text prompt for the model.
            system_prompt (str, optional): An optional system prompt.
            **generation_kwargs: Call-specific keyword arguments to pass to the model's generate method.
                                 These override all other defaults.

        Returns:
            str | list[str]: The model's generated response(s).
        """
        try:
            # Explicitly load model and tokenizer
            self._load_model_and_tokenizer()
            for i in range(torch.cuda.device_count()):
                print(f"GPU {i} allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
                print(f"GPU {i} reserved: {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")

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

            for i in range(torch.cuda.device_count()):
                print(f"GPU {i} allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
                print(f"GPU {i} reserved: {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")
            with torch.no_grad():
                generated_ids_full = self.model.generate(
                    **model_inputs,
                    **final_params
                )
                if isinstance(generated_ids_full, torch.Tensor):
                    generated_ids_full = generated_ids_full.cpu()

            
            input_ids_len = model_inputs["input_ids"].shape[1]
            
            responses = []
            for i in range(num_return_sequences):
                current_sequence_ids = generated_ids_full[i, input_ids_len:]
                
                # Decode the full response
                full_response_text = self.tokenizer.decode(current_sequence_ids, skip_special_tokens=True)
                
                # Attempt to find and remove the thinking part
                # The token ID for '</think>' is 151668 in Qwen models.
                # This part is specific to models that output thinking tags.
                output_ids = current_sequence_ids.tolist()
                try:
                    # Find the index of the last '</think>' token
                    # We search from the end to handle multiple thinking blocks if they exist
                    index_end_think_token = len(output_ids) - output_ids[::-1].index(151668)
                    
                    # The content after '</think>' is the actual response
                    # We add 1 to the index to start decoding *after* the '</think>' token
                    response_text = self.tokenizer.decode(output_ids[index_end_think_token:], skip_special_tokens=True).strip()
                except ValueError:
                    # If '</think>' is not found, use the full response
                    response_text = full_response_text.strip()

                responses.append(response_text)

            return responses if num_return_sequences > 1 else responses[0]

        except Exception as e:
            print(f"Error during model query for '{self.model_name}': {e}")
            return f"Error generating response: {e}"
        finally:
            # Explicitly unload model and tokenizer
            self.unload_model()