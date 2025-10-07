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

    def get_top_n_similar(self, query: str, candidates: list[dict], top_n: int = None) -> list[dict]:
        """
        Calculates semantic similarity for all candidates and returns the top N.

        Args:
            query (str): The query text.
            candidates (list[dict]): A list of candidate dictionaries, each must have a "value" key.
            top_n (int, optional): The number of top results to return. If None, returns all candidates.

        Returns:
            list[dict]: A sorted list of candidates with an added 'similarity' key.
        """
        if not query or not candidates:
            return []

        candidate_values = [c['value'] for c in candidates]
        similarity_scores = self.calculate_cosine_similarity(query, candidate_values)
        
        for i, candidate in enumerate(candidates):
            candidate['embedding_similarity'] = similarity_scores[i]
        
        candidates.sort(key=lambda x: x['embedding_similarity'], reverse=True)
        
        if top_n:
            return candidates[:top_n]
    
        def get_similar_by_threshold(self, query: str, candidates: list[dict], threshold: float = 0.6) -> list[dict]:
            """
            Gets candidates with a semantic similarity score above a certain threshold.
    
            Args:
                query (str): The query text.
                candidates (list[dict]): A list of candidate dictionaries, each must have a "value" key.
                threshold (float): The minimum similarity threshold.
    
            Returns:
                list[dict]: A list of candidates with their 'embedding_similarity' score, exceeding the threshold.
            """
            if not query or not candidates:
                return []
    
            candidate_values = [c['value'] for c in candidates]
            similarity_scores = self.calculate_cosine_similarity(query, candidate_values)
            
            results = []
            for i, candidate in enumerate(candidates):
                if similarity_scores[i] >= threshold:
                    candidate['embedding_similarity'] = similarity_scores[i]
                    results.append(candidate)
            
            results.sort(key=lambda x: x['embedding_similarity'], reverse=True)
            return results
        return candidates