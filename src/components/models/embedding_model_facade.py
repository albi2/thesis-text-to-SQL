import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

import torch
from transformers import AutoTokenizer, AutoModel
from abc import ABC, abstractmethod
from typing import List, Union, Optional, Dict
import logging
from huggingface_hub import snapshot_download
from util.constants import HuggingFaceModelConstants
import gc
import torch.nn.functional as F
from torch import Tensor

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Consistent cache directory
os.environ['HF_HUB_CACHE'] = "/var/tmp/ge62nok"
os.environ['HF_HOME'] = "/var/tmp/ge62nok"
os.environ['PYTORCH_NVML_BASED_CUDA_CHECK'] = "1"

def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    """
    Applies last token pooling to the hidden states.
    Used for models that output sequence of hidden states (like AutoModel).
    """
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]

def get_detailed_instruct(task_description: str, query: str) -> str:
    """
    Formats an instruction and query into a single string for models that require it.
    """
    return f'Instruct: {task_description}\nQuery:{query}'

class BaseEmbeddingModelFacade(ABC):
    """
    Abstract base class for embedding model facades.
    """
    def __init__(self, model_name_or_path: str, device: Optional[str] = None, **kwargs):
        self.model_name_or_path = model_name_or_path
        self.device = device
        self._model = None # Lazy loaded
        self._tokenizer = None # Lazy loaded
        self.model_kwargs = kwargs

    @property
    def model(self):
        """Property to access the model, triggers loading on first access."""
        if self._model is None:
            self._load_model(**self.model_kwargs)
        return self._model

    @property
    def tokenizer(self):
        """Property to access the tokenizer, triggers loading on first access."""
        if self._tokenizer is None:
            self._load_model(**self.model_kwargs)
        return self._tokenizer

    @abstractmethod
    def _load_model(self, **kwargs) -> None:
        """Loads the underlying embedding model and tokenizer."""
        pass

    @abstractmethod
    def encode(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Generates embeddings for a list of texts."""
        pass

    @abstractmethod
    def encode_single(self, text: str, **kwargs) -> List[float]:
        """Generates an embedding for a single text."""
        pass


class HuggingFaceEmbeddingFacade(BaseEmbeddingModelFacade):
    """
    A facade for generating embeddings using models from the Hugging Face transformers library.
    """
    def __init__(self,
                 model_name_or_path: str = None,
                 device: str = None,
                 **kwargs):
        """
        Initializes the HuggingFaceEmbeddingFacade.

        If model_name_or_path is None, it attempts to download the
        DEFAULT_EMBEDDING_MODEL to DEFAULT_EMBEDDING_MODEL_PATH and use that path.
        Otherwise, it uses the provided model_name_or_path.

        Args:
            model_name_or_path (str): The name or path of the Hugging Face model.
            device (str): The device to run the model on (e.g., "cpu", "cuda").
            **kwargs: Additional keyword arguments for the superclass and _load_model.
        """
        effective_model_name = model_name_or_path or HuggingFaceModelConstants.DEFAULT_EMBEDDING_MODEL_PATH
        super().__init__(model_name_or_path=effective_model_name, device=device, **kwargs)

        # Use default model and path
        default_model_repo_id = HuggingFaceModelConstants.DEFAULT_EMBEDDING_MODEL

        # Ensure the target directory exists

        try:
            logger.info(f"Downloading/verifying {default_model_repo_id} to {effective_model_name}...")
            os.makedirs(effective_model_name, exist_ok=True)
            snapshot_download(
                repo_id=default_model_repo_id,
                local_dir=effective_model_name,
                # consider adding allow_patterns or ignore_patterns if needed
            )
            logger.info(f"Successfully downloaded/verified {default_model_repo_id} to {effective_model_name}.")
        except Exception as e:
            logger.error(f"Error downloading default embedding model {default_model_repo_id} to {effective_model_name}: {e}", exc_info=True)
        

    def _load_model(self, model_kwargs: Optional[Dict] = None, tokenizer_kwargs: Optional[Dict] = None, trust_remote_code: bool = True) -> None:
        """
        Loads the Hugging Face AutoModel and AutoTokenizer.

        Args:
            model_kwargs (Optional[Dict]): Keyword arguments to pass to the AutoModel.from_pretrained constructor.
                                           Example: {"attn_implementation": "flash_attention_2", "device_map": "auto"}
            tokenizer_kwargs (Optional[Dict]): Keyword arguments for the AutoTokenizer.from_pretrained.
                                               Example: {"padding_side": "left"}
            trust_remote_code (bool): Whether to trust remote code when loading the model. Default True.
        """
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i} allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
            print(f"GPU {i} reserved: {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")
        logger.info(f"--- Starting lazy load for HuggingFaceEmbeddingFacade: {self.model_name_or_path} ---")
        effective_tokenizer_kwargs = tokenizer_kwargs if tokenizer_kwargs is not None else {}

        logger.info(f"Loading tokenizer for '{self.model_name_or_path}'...")
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name_or_path,
                trust_remote_code=trust_remote_code,
                **effective_tokenizer_kwargs
            )
            if self._tokenizer.pad_token_id is None:
                self._tokenizer.pad_token_id = self._tokenizer.eos_token_id
                logger.info(f"Tokenizer pad_token_id set to eos_token_id: {self._tokenizer.eos_token_id}")
            logger.info(f"Tokenizer '{self.model_name_or_path}' loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading tokenizer '{self.model_name_or_path}': {e}", exc_info=True)
            raise

        logger.info(f"Loading model '{self.model_name_or_path}'")

        # Determine device mapping
        if not torch.cuda.is_available():
            # print(f"Warning: CUDA not available. Model '{self.model_name_or_path}' will run on CPU.")
            # self.device_map_config = None
            raise RuntimeError("No GPU found! Please make sure a CUDA-enabled GPU is available.")
        else:
            self.device_map_config = "auto"
            print(f"{torch.cuda.device_count()} GPU(s) detected. Using device_map='auto' for '{self.model_name_or_path}'.")


        try:
            self._model = AutoModel.from_pretrained(
                self.model_name_or_path,
                device_map=self.device_map_config,
                torch_dtype=torch.bfloat16
            )
            self._model = self._model.to_bettertransformer()
            logger.info(f"Model '{self.model_name_or_path}' loaded successfully.")
            if self.device_map_config == "auto" and hasattr(self._model, 'hf_device_map'):
                 logger.info(f"Model device map: {self._model.hf_device_map}")
            elif hasattr(self._model, 'device'):
                 logger.info(f"Model loaded on device: {self._model.device}")

        except Exception as e:
            logger.error(f"Error loading model '{self.model_name_or_path}': {e}", exc_info=True)
            raise e
        
        logger.info(f"--- Finished lazy load for HuggingFaceEmbeddingFacade: {self.model_name_or_path} ---")

    def unload_model(self):
        """Unloads the model and tokenizer to free up memory."""
        if self._model is None and self._tokenizer is None:
            logger.info(f"Embedding model '{self.model_name_or_path}' is not loaded, nothing to unload.")
            return
            
        logger.info(f"Unloading embedding model and tokenizer for '{self.model_name_or_path}'...")
        if self._model is not None:
            del self._model
            self._model = None
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                torch.cuda.set_device(i)
                torch.cuda.empty_cache() 
                torch.cuda.ipc_collect()
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
                gc.collect()
        

        for i in range(torch.cuda.device_count()):
            torch.cuda.memory._dump_snapshot()  # Debug info
            torch.cuda.reset_accumulated_memory_stats(i)
            torch.cuda.reset_peak_memory_stats(i)

        # if hasattr(torch.cuda, 'memory'):
        #     for i in range(torch.cuda.device_count()):
        #         torch.cuda.set_device(i)
        #         # This forces the allocator to release unused blocks
        #         torch.cuda.memory.empty_cache()

        for i in range(torch.cuda.device_count()):
            print(f"GPU {i} allocated: {torch.cuda.memory_allocated(i) / 1024**3:.2f} GB")
            print(f"GPU {i} reserved: {torch.cuda.memory_reserved(i) / 1024**3:.2f} GB")
        logger.info(f"Embedding model '{self.model_name_or_path}' unloaded successfully.")

    def encode(self, texts: List[str], batch_size: int = 32, normalize_embeddings: bool = True, **kwargs) -> List[List[float]]:
        """
        Generates embeddings for a list of texts using the Hugging Face model.
        The model and tokenizer are loaded at the beginning of this method and unloaded at the end.

        Args:
            texts (List[str]): A list of texts to embed.
            batch_size (int): The batch size for processing texts.
            normalize_embeddings (bool): Whether to normalize embeddings to unit length.
            **kwargs: Additional arguments for the model's encode method (e.g., max_length).

        Returns:
            List[List[float]]: A list of embeddings.
        """
        try:
            self._load_model(model_kwargs=self.model_kwargs.get('model_kwargs'), tokenizer_kwargs=self.model_kwargs.get('tokenizer_kwargs'), trust_remote_code=self.model_kwargs.get('trust_remote_code', True))
            logger.debug(f"Encoding {len(texts)} texts with batch_size={batch_size}, normalize={normalize_embeddings}")

            # Tokenize the input texts
            batch_dict = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=kwargs.get("max_length", 8192), # Default max_length
                return_tensors="pt",
            )
            
            # Move batch to model's device
            if self.model.device.type == 'cuda':
                batch_dict = {k: v.to(self.model.device) for k, v in batch_dict.items()}

            with torch.no_grad():
                outputs = self.model(**batch_dict)
            
            # Apply pooling
            embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

            # Normalize embeddings
            if normalize_embeddings:
                embeddings = F.normalize(embeddings, p=2, dim=1)

            # Move embeddings to CPU and convert to list of lists
            if isinstance(embeddings, torch.Tensor):
                embeddings = embeddings.cpu().tolist()
            return embeddings
        finally:
            self.unload_model()

    def encode_single(self, text: str, normalize_embeddings: bool = True, **kwargs) -> List[float]:
        """
        Generates an embedding for a single text using the Hugging Face model.
        The model and tokenizer are loaded at the beginning of this method and unloaded at the end.

        Args:
            text (str): The text to embed.
            normalize_embeddings (bool): Whether to normalize the embedding to unit length.
            **kwargs: Additional arguments for the model's encode method (e.g., max_length).

        Returns:
            List[float]: The embedding for the text.
        """
        try:
            self._load_model(model_kwargs=self.model_kwargs.get('model_kwargs'), tokenizer_kwargs=self.model_kwargs.get('tokenizer_kwargs'), trust_remote_code=self.model_kwargs.get('trust_remote_code', True))
            logger.debug(f"Encoding single text, normalize={normalize_embeddings}")

            # Tokenize the input text
            batch_dict = self.tokenizer(
                [text], # encode expects a list
                padding=True,
                truncation=True,
                max_length=kwargs.get("max_length", 8192), # Default max_length
                return_tensors="pt",
            )

            # Move batch to model's device
            if self.model.device.type == 'cuda':
                batch_dict = {k: v.to(self.model.device) for k, v in batch_dict.items()}

            with torch.no_grad():
                outputs = self.model(**batch_dict)
            
            # Apply pooling
            embedding = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

            # Normalize embedding
            if normalize_embeddings:
                embedding = F.normalize(embedding, p=2, dim=1)

            # Move embedding to CPU and convert to list, then take the first element
            if isinstance(embedding, torch.Tensor):
                embedding = embedding.cpu().tolist()
            return embedding[0]
        finally:
            self.unload_model()

    def similarity(self, embeddings1: Union[torch.Tensor, List[List[float]]], embeddings2: Union[torch.Tensor, List[List[float]]]) -> torch.Tensor:
        """
        Computes cosine similarity between two sets of embeddings.

        Args:
            embeddings1 (Union[torch.Tensor, List[List[float]]]): First set of embeddings.
            embeddings2 (Union[torch.Tensor, List[List[float]]]): Second set of embeddings.

        Returns:
            torch.Tensor: A tensor containing similarity scores.
        """
        if not isinstance(embeddings1, torch.Tensor):
            embeddings1 = torch.tensor(embeddings1)
        if not isinstance(embeddings2, torch.Tensor):
            embeddings2 = torch.tensor(embeddings2)
            
        return F.cosine_similarity(embeddings1, embeddings2)