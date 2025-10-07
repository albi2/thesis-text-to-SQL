from typing import List, Dict, Any
from colbert import ColbertReranker

class Reranker:
    def __init__(self, checkpoint='colbert-ir/colbertv2.0'):
        self.reranker = ColbertReranker(checkpoint=checkpoint)

    def rerank(self, query: str, documents: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
        """
        Reranks a list of documents based on a query using Colbert v2.

        Args:
            query: The query string.
            documents: A list of documents to rerank. Each document is a dictionary.
            k: The number of documents to return.

        Returns:
            A list of reranked documents.
        """
        doc_texts = [doc["description"] for doc in documents]
        
        reranked_indices = self.reranker.rerank(query, doc_texts)
        
        return [documents[i] for i in reranked_indices][:k]