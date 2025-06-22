import torch
from sentence_transformers import SentenceTransformer
from abc import ABC, abstractmethod
import os
from typing import List, Union, Optional, Dict
import logging
from huggingface_hub import snapshot_download
from util.constants import HuggingFaceModelConstants
import gc

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Consistent cache directory
DEFAULT_HF_CACHE_DIR = "/var/tmp/ge62nok" # Aligns with other facades if they use this
# sentence-transformers uses its own caching mechanism by default, often ~/.cache/torch/sentence_transformers/
# We can specify a cache_folder to SentenceTransformer if we want to override it.
# For now, let's allow ST to use its default or respect HF_HOME if set.
HF_HOME = os.environ.get('HF_HOME', os.path.join(os.path.expanduser("~"), ".cache", "huggingface"))
SENTENCE_TRANSFORMERS_HOME = os.environ.get('SENTENCE_TRANSFORMERS_HOME', os.path.join(HF_HOME, 'sentence_transformers'))
os.makedirs(SENTENCE_TRANSFORMERS_HOME, exist_ok=True)

class BaseEmbeddingModelFacade(ABC):
    """
    Abstract base class for embedding model facades.
    """
    def __init__(self, model_name_or_path: str, device: Optional[str] = None, **kwargs):
        self.model_name_or_path = model_name_or_path
        self.device = device
        self._model = None # Lazy loaded
        self.model_kwargs = kwargs

    @property
    def model(self):
        """Property to access the model, triggers loading on first access."""
        if self._model is None:
            self._load_model(**self.model_kwargs)
        return self._model

    @abstractmethod
    def _load_model(self, **kwargs) -> any:
        """Loads the underlying embedding model."""
        pass

    @abstractmethod
    def encode(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Generates embeddings for a list of texts."""
        pass

    @abstractmethod
    def encode_single(self, text: str, **kwargs) -> List[float]:
        """Generates an embedding for a single text."""
        pass


class SentenceTransformerEmbeddingFacade(BaseEmbeddingModelFacade):
    """
    A facade for generating embeddings using models from the sentence-transformers library.
    """
    def __init__(self,
                 model_name_or_path: Optional[str] = None,
                 device: Optional[str] = None,
                 **kwargs):
        """
        Initializes the SentenceTransformerEmbeddingFacade.

        If model_name_or_path is None, it attempts to download the
        DEFAULT_EMBEDDING_MODEL to DEFAULT_EMBEDDING_MODEL_PATH and use that path.
        Otherwise, it uses the provided model_name_or_path.

        Args:
            model_name_or_path (Optional[str]): The name or path of the SentenceTransformer model.
            device (Optional[str]): The device to run the model on (e.g., "cpu", "cuda").
            **kwargs: Additional keyword arguments for the superclass and _load_model.
        """
        model_identifier_for_load: str

        if model_name_or_path is None:
            # Use default model and path
            default_model_repo_id = HuggingFaceModelConstants.DEFAULT_EMBEDDING_MODEL
            default_local_path = HuggingFaceModelConstants.DEFAULT_EMBEDDING_MODEL_PATH

            logger.info(f"No model_name_or_path provided. Attempting to use default embedding model: {default_model_repo_id}")
            logger.info(f"Target local path for default model: {default_local_path}")

            # Ensure the target directory exists
            os.makedirs(default_local_path, exist_ok=True)

            # Check if model might already be there (simple check, snapshot_download handles actual download/update)
            # This is more for logging context than for skipping download, as snapshot_download is idempotent.
            if not os.listdir(default_local_path): # Basic check if directory is empty
                 logger.info(f"Local path {default_local_path} appears empty or new. Proceeding with download/verification.")
            else:
                 logger.info(f"Local path {default_local_path} exists and is not empty. snapshot_download will verify/update.")

            try:
                logger.info(f"Downloading/verifying {default_model_repo_id} to {default_local_path}...")
                snapshot_download(
                    repo_id=default_model_repo_id,
                    local_dir=default_local_path,
                    # consider adding allow_patterns or ignore_patterns if needed
                )
                logger.info(f"Successfully downloaded/verified {default_model_repo_id} to {default_local_path}.")
                model_identifier_for_load = default_local_path
            except Exception as e:
                logger.error(f"Error downloading default embedding model {default_model_repo_id} to {default_local_path}: {e}", exc_info=True)
                logger.warning(f"Falling back to using model name '{default_model_repo_id}' directly for loading due to download error.")
                model_identifier_for_load = default_model_repo_id
        else:
            # User provided a specific model name or path
            logger.info(f"Using provided model_name_or_path: {model_name_or_path}")
            model_identifier_for_load = model_name_or_path
        
        super().__init__(model_name_or_path=model_identifier_for_load, device=device, **kwargs)

    def _load_model(self, model_kwargs: Optional[Dict] = None, tokenizer_kwargs: Optional[Dict] = None, trust_remote_code: bool = True) -> SentenceTransformer:
        """
        Loads the SentenceTransformer model.

        Args:
            model_kwargs (Optional[Dict]): Keyword arguments to pass to the SentenceTransformer model constructor.
                                           Example: {"attn_implementation": "flash_attention_2", "device_map": "auto"}
            tokenizer_kwargs (Optional[Dict]): Keyword arguments for the tokenizer.
                                               Example: {"padding_side": "left"}
            trust_remote_code (bool): Whether to trust remote code when loading the model. Default True.
        """
        logger.info(f"--- Starting lazy load for SentenceTransformer: {self.model_name_or_path} ---")
        effective_model_kwargs = model_kwargs if model_kwargs is not None else {}
        effective_tokenizer_kwargs = tokenizer_kwargs if tokenizer_kwargs is not None else {}

        # Default to 'auto' device_map if GPUs are available and not specified
        if 'device_map' not in effective_model_kwargs and self.device is None and torch.cuda.is_available():
            effective_model_kwargs['device_map'] = 'cuda:0'
        elif self.device and 'device_map' not in effective_model_kwargs : # if specific device is given
             effective_model_kwargs['device'] = self.device

        effective_model_kwargs["torch_dtype"] = torch.bfloat16

        logger.info(f"Loading SentenceTransformer model: '{self.model_name_or_path}' with device='{self.device or 'auto (if GPU)'}'")
        logger.info(f"Model kwargs: {effective_model_kwargs}")
        logger.info(f"Tokenizer kwargs: {effective_tokenizer_kwargs}")
        
        try:
            self._model = SentenceTransformer(
                self.model_name_or_path,
                cache_folder=SENTENCE_TRANSFORMERS_HOME,
                trust_remote_code=trust_remote_code, # Important for some models like Qwen
                model_kwargs=effective_model_kwargs if effective_model_kwargs else None,
                tokenizer_kwargs=effective_tokenizer_kwargs if effective_tokenizer_kwargs else None,
                device=self.device # Explicitly pass device if set, otherwise ST handles it (e.g. via device_map)
            )
            logger.info(f"SentenceTransformer model '{self.model_name_or_path}' loaded successfully.")
            if hasattr(self._model, '_target_device'):
                 logger.info(f"Model target device: {model._target_device}")

        except Exception as e:
            logger.error(f"Error loading SentenceTransformer model '{self.model_name_or_path}': {e}", exc_info=True)
            # Try without flash_attention if it was the cause
            if "attn_implementation" in effective_model_kwargs and "flash_attention" in effective_model_kwargs["attn_implementation"]:
                logger.warning("Attempting to load model without flash_attention...")
                del effective_model_kwargs["attn_implementation"]
                try:
                    self._model = SentenceTransformer(
                        self.model_name_or_path,
                        cache_folder=SENTENCE_TRANSFORMERS_HOME,
                        trust_remote_code=trust_remote_code,
                        model_kwargs=effective_model_kwargs if effective_model_kwargs else None,
                        tokenizer_kwargs=effective_tokenizer_kwargs if effective_tokenizer_kwargs else None,
                        device=self.device
                    )
                    logger.info(f"Model '{self.model_name_or_path}' loaded successfully without flash_attention.")
                except Exception as e2:
                    logger.error(f"Still failed to load model '{self.model_name_or_path}' without flash_attention: {e2}", exc_info=True)
                    raise e2
            else:
                raise e
        
        logger.info(f"--- Finished lazy load for SentenceTransformer: {self.model_name_or_path} ---")

    def unload_model(self):
        """Unloads the model to free up memory."""
        if self._model is None:
            logger.info(f"Embedding model '{self.model_name_or_path}' is not loaded, nothing to unload.")
            return
            
        logger.info(f"Unloading embedding model '{self.model_name_or_path}'...")
        del self._model
        self._model = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()    
            torch.cuda.synchronize()  # Ensur
        logger.info(f"Embedding model '{self.model_name_or_path}' unloaded successfully.")

    def encode(self, texts: List[str], batch_size: int = 32, normalize_embeddings: bool = True, **kwargs) -> List[List[float]]:
        """
        Generates embeddings for a list of texts.
        The model is loaded at the beginning of this method and unloaded at the end.

        Args:
            texts (List[str]): A list of texts to embed.
            batch_size (int): The batch size for processing texts.
            normalize_embeddings (bool): Whether to normalize embeddings to unit length.
            **kwargs: Additional arguments for the model's encode method.

        Returns:
            List[List[float]]: A list of embeddings.
        """
        try:
            self._load_model(model_kwargs=self.model_kwargs.get('model_kwargs'), tokenizer_kwargs=self.model_kwargs.get('tokenizer_kwargs'), trust_remote_code=self.model_kwargs.get('trust_remote_code', True))
            logger.debug(f"Encoding {len(texts)} texts with batch_size={batch_size}, normalize={normalize_embeddings}")
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize_embeddings,
                **kwargs
            )
            # Move embeddings to CPU and convert to list of lists
            if isinstance(embeddings, torch.Tensor):
                embeddings = embeddings.cpu().tolist()
                del embeddings
            return embeddings
        finally:
            self.unload_model()

    def encode_single(self, text: str, normalize_embeddings: bool = True, **kwargs) -> List[float]:
        """
        Generates an embedding for a single text.
        The model is loaded at the beginning of this method and unloaded at the end.

        Args:
            text (str): The text to embed.
            normalize_embeddings (bool): Whether to normalize the embedding to unit length.
            **kwargs: Additional arguments for the model's encode method.

        Returns:
            List[float]: The embedding for the text.
        """
        try:
            self._load_model(model_kwargs=self.model_kwargs.get('model_kwargs'), tokenizer_kwargs=self.model_kwargs.get('tokenizer_kwargs'), trust_remote_code=self.model_kwargs.get('trust_remote_code', True))
            logger.debug(f"Encoding single text, normalize={normalize_embeddings}")
            embedding = self.model.encode(
                [text], # encode expects a list
                normalize_embeddings=normalize_embeddings,
                **kwargs
            )
            # Move embedding to CPU and convert to list, then take the first element
            if isinstance(embedding_gpu, torch.Tensor):
                embedding = embedding.cpu().tolist()
            return embedding[0]
        finally:
            self.unload_model()

    def similarity(self, embeddings1: Union[torch.Tensor, List[List[float]]], embeddings2: Union[torch.Tensor, List[List[float]]]) -> torch.Tensor:
        """
        Computes cosine similarity between two sets of embeddings.
        Requires `sentence-transformers` to handle the underlying similarity calculation.

        Args:
            embeddings1 (Union[torch.Tensor, List[List[float]]]): First set of embeddings.
            embeddings2 (Union[torch.Tensor, List[List[float]]]): Second set of embeddings.

        Returns:
            torch.Tensor: A tensor containing similarity scores.
        """
        from sentence_transformers.util import cos_sim # Import here to keep dependency optional if only encoding
        
        if not isinstance(embeddings1, torch.Tensor):
            embeddings1 = torch.tensor(embeddings1)
        if not isinstance(embeddings2, torch.Tensor):
            embeddings2 = torch.tensor(embeddings2)
            
        return cos_sim(embeddings1, embeddings2)