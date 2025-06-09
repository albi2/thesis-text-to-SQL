"""
This module defines the SemanticSimilarityUtil class for calculating semantic similarity
using sentence embeddings.
"""
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch # Often a dependency for sentence-transformers

class SemanticSimilarityUtil:
    """
    Utility class for calculating semantic similarity between texts using sentence embeddings.

    This class utilizes a pre-trained model from the sentence-transformers library
    to generate embeddings and then computes their cosine similarity.
    """
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initializes the SemanticSimilarityUtil with a specified sentence embedding model.

        Args:
            model_name (str): The name of the sentence-transformer model to use.
                              Defaults to 'sentence-transformers/all-MiniLM-L6-v2'.
        """
        # Check if CUDA is available and set the device accordingly
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name, device=self.device)
        print(f"SemanticSimilarityUtil initialized with model '{model_name}' on device '{self.device}'.")

    def calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates the cosine similarity between the embeddings of two texts.

        Args:
            text1 (str): The first text.
            text2 (str): The second text.

        Returns:
            float: The cosine similarity score between the two texts, ranging from -1 to 1.
                   Returns 0.0 if either text is empty or None.
        """
        if not text1 or not text2:
            return 0.0

        embeddings = self.model.encode([text1, text2], convert_to_tensor=True, device=self.device)
        
        # cosine_similarity expects 2D arrays.
        # embeddings[0] and embeddings[1] are 1D tensors (vectors).
        # We need to reshape them to 2D (1, embedding_dim) before passing to cosine_similarity.
        emb1 = embeddings[0].unsqueeze(0)
        emb2 = embeddings[1].unsqueeze(0)
        
        # Calculate cosine similarity
        # The result is a 2x2 matrix if we pass both embeddings directly,
        # or a 1x1 matrix if we pass them as emb1, emb2.
        # We want the similarity between emb1 and emb2, which is a single value.
        similarity_matrix = cosine_similarity(emb1.cpu().numpy(), emb2.cpu().numpy())
        
        return float(similarity_matrix[0, 0])