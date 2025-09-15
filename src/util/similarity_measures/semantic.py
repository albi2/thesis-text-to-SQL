"""
This module defines the SemanticSimilarityUtil class for calculating semantic similarity
using sentence embeddings.
"""
import os
os.environ['PYTORCH_NVML_BASED_CUDA_CHECK'] = "1"

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from components.models.embedding_model_facade import HuggingFaceEmbeddingFacade

class SemanticSimilarityUtil:
    """
    Utility class for calculating semantic similarity between texts using sentence embeddings.
    """
    def __init__(self):
        """
        Initializes the SemanticSimilarityUtil.
        """
        self.embedding_facade = HuggingFaceEmbeddingFacade()

    def calculate_cosine_similarity(self, query: str, candidates: list[str]) -> np.ndarray:
        """
        Calculates the cosine similarity between a query and a list of candidates.

        Args:
            query (str): The query text.
            candidates (list[str]): A list of candidate texts.

        Returns:
            np.ndarray: An array of cosine similarity scores.
        """
        if not query or not candidates:
            return np.array([])

        query_embedding = self.embedding_facade.encode_single(query)
        candidate_embeddings = self.embedding_facade.encode(candidates)

        similarity_matrix = cosine_similarity([query_embedding], candidate_embeddings)
        
        return similarity_matrix[0]

    def get_top_n_similar(self, query: str, candidates: list[dict], top_n: int = 5) -> list[dict]:
        """
        Gets the top-n most similar candidates to a query.

        Args:
            query (str): The query text.
            candidates (list[dict]): A list of candidate dictionaries, where each dictionary contains the value and its metadata.
            top_n (int): The number of top results to return.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains a candidate and its similarity score.
        """
        if not query or not candidates:
            return []

        candidate_values = [c['value'] for c in candidates]
        similarity_scores = self.calculate_cosine_similarity(query, candidate_values)
        
        # Add similarity score to each candidate dictionary
        for i, candidate in enumerate(candidates):
            candidate['similarity'] = similarity_scores[i]
        
        # Sort by score in descending order
        candidates.sort(key=lambda x: x['similarity'], reverse=True)
        
        return candidates[:top_n]