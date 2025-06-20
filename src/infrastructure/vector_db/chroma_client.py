import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from typing import List, Dict, Optional
import logging
from chromadb.config import Settings

# Assuming BaseEmbeddingModelFacade and SentenceTransformerEmbeddingFacade are importable
# from ..components.models.embedding_model_facade import BaseEmbeddingModelFacade
# Adjust the import path based on your project structure.
# For now, let's assume it's in a place Python can find, or we'll define a placeholder.
# If this script is run directly, the relative import will fail.
try:
    from components.models.embedding_model_facade import BaseEmbeddingModelFacade, SentenceTransformerEmbeddingFacade
except ImportError:
    logging.warning("Could not import BaseEmbeddingModelFacade. Define a placeholder if running standalone for type hinting.")
    # Placeholder for type hinting if the actual class isn't found (e.g. running script directly)
    class BaseEmbeddingModelFacade:
        def encode(self, texts: List[str], **kwargs) -> List[List[float]]:
            raise NotImplementedError
        def encode_single(self, text: str, **kwargs) -> List[float]:
            raise NotImplementedError
    class SentenceTransformerEmbeddingFacade(BaseEmbeddingModelFacade): # type: ignore
        pass


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class FacadeEmbeddingFunction(EmbeddingFunction):
    """
    A ChromaDB-compatible embedding function that wraps our BaseEmbeddingModelFacade.
    """
    def __init__(self, facade: BaseEmbeddingModelFacade, prompt_name: Optional[str] = None, normalize_embeddings: bool = True):
        self._facade = facade
        self._prompt_name = prompt_name # For models like Qwen that might use different prompts for query/doc
        self._normalize_embeddings = normalize_embeddings
        logger.info(f"FacadeEmbeddingFunction initialized with facade: {type(facade).__name__}, prompt_name: '{prompt_name}', normalize: {normalize_embeddings}")

    def __call__(self, texts: Documents) -> Embeddings:
        """
        Generates embeddings for the given documents.

        Args:
            texts (Documents): A list of texts (strings) to embed.

        Returns:
            Embeddings: A list of embeddings, where each embedding is a list of floats.
        """
        if not texts:
            return []
        # The facade's encode method should handle batching if necessary.
        # Pass prompt_name and normalize_embeddings to the facade's encode method.
        embeddings = self._facade.encode(
            texts, 
            prompt_name=self._prompt_name, 
            normalize_embeddings=self._normalize_embeddings
        )
        logger.debug(f"Generated {len(embeddings)} embeddings using FacadeEmbeddingFunction.")
        return embeddings


class ChromaClient:
    """
    A client for interacting with a ChromaDB instance, using a provided embedding model facade.
    """
    def __init__(self, embedding_facade: BaseEmbeddingModelFacade, host: str = "localhost", port: int = 8000):
        """
        Initializes the ChromaClient.

        Args:
            embedding_facade (BaseEmbeddingModelFacade): An instance of an embedding model facade
                                                         (e.g., SentenceTransformerEmbeddingFacade).
            host (str): The host of the ChromaDB server.
            port (int): The port of the ChromaDB server.
        """
        self.client = chromadb.HttpClient(host=host, port=port, settings=Settings(anonymized_telemetry=False))
        self.embedding_facade = embedding_facade
        logger.info(f"ChromaClient initialized with host='{host}', port={port}, facade='{type(embedding_facade).__name__}'")

    def get_or_create_collection(self, collection_name: str, prompt_name_for_embedding_fn: Optional[str] = None, normalize_embeddings_for_fn: bool = True) -> chromadb.api.models.Collection.Collection:
        """
        Gets an existing collection or creates it if it doesn't exist.
        The collection will use an embedding function based on the facade provided to the ChromaClient.

        Args:
            collection_name (str): The name of the collection.
            prompt_name_for_embedding_fn (Optional[str]): Specific prompt_name to use for this collection's
                                                          embedding function (e.g., "query" or "document").
                                                          Passed to the FacadeEmbeddingFunction.
            normalize_embeddings_for_fn (bool): Whether to normalize embeddings for this collection's
                                                embedding function. Passed to FacadeEmbeddingFunction.


        Returns:
            chromadb.api.models.Collection.Collection: The collection object.
        """
        # Create a new instance of our custom embedding function for this collection,
        # potentially with specific settings like prompt_name.
        custom_embedding_function = FacadeEmbeddingFunction(
            facade=self.embedding_facade,
            prompt_name=prompt_name_for_embedding_fn,
            normalize_embeddings=normalize_embeddings_for_fn
        )
        
        logger.info(f"Getting or creating collection '{collection_name}' with custom embedding function.")
        # self.client.delete_collection(name=collection_name)
        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=custom_embedding_function
            # metadata={"hnsw:space": "cosine"} # Example: if you want to specify cosine distance
        )
        logger.info(f"Collection '{collection.name}' (ID: {collection.id}) retrieved/created with {collection.count()} documents.")
        return collection

    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict], ids: List[str]) -> None:
        """
        Adds documents to a specified collection.
        The collection must already exist and will use the embedding function it was created with.

        Args:
            collection_name (str): The name of the collection.
            documents (List[str]): A list of documents (texts) to add.
            metadatas (List[Dict]): A list of metadata dictionaries corresponding to the documents.
            ids (List[str]): A list of unique IDs for the documents.
        """
        collection = self.client.get_collection(name=collection_name)
        logger.info(f"Generating embeddings for {len(documents)} documents before adding to collection '{collection_name}'.")
        
        # Generate embeddings using the facade
        embeddings = self.embedding_facade.encode(
            documents,
            prompt_name="document", # Assuming "document" is a suitable prompt for document embeddings
            normalize_embeddings=True # Typically, document embeddings are normalized
        )

        logger.info(f"Adding {len(documents)} documents to collection '{collection_name}'.")
        collection.add(
            embeddings=embeddings,
            documents=documents, # Keep documents for retrieval, even if embeddings are pre-computed
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Documents added. Collection '{collection_name}' now has {collection.count()} documents.")


    def query_collection(self, collection_name: str, query_texts: List[str], n_results: int = 5, query_prompt_name: Optional[str] = "query", **kwargs) -> Dict:
        """
        Queries a collection.

        Args:
            collection_name (str): The name of the collection.
            query_texts (List[str]): A list of query texts.
            n_results (int): The number of results to return for each query.
            query_prompt_name (Optional[str]): The prompt_name to use for encoding the query_texts,
                                               if the underlying model supports it (e.g., "query" for Qwen).
                                               This is passed to the facade via a temporary embedding list.
            **kwargs: Additional arguments for the query.

        Returns:
            Dict: A dictionary containing the query results.
        """
        collection = self.client.get_collection(name=collection_name)
        
        # For querying, ChromaDB expects query_embeddings. We generate these using our facade,
        # potentially with a specific "query" prompt if applicable.
        query_embeddings = self.embedding_facade.encode(
            query_texts, 
            prompt_name=query_prompt_name, 
            normalize_embeddings=True # Typically, queries are normalized for cosine similarity
        )
        
        logger.info(f"Querying collection '{collection_name}' with {len(query_texts)} texts, n_results={n_results}, query_prompt_name='{query_prompt_name}'.")
        results = collection.query(
            query_embeddings=query_embeddings, # Pass the generated embeddings
            n_results=n_results,
            include=['metadatas', 'documents', 'distances'], # Ensure we get these back
            **kwargs
        )
        logger.debug(f"Query results: {results}")
        return results