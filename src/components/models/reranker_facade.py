from colbert.infra import Run, RunConfig
from colbert import Rerank
from typing import List, Dict, Any

class Reranker:
    def __init__(self):
        self.reranker = Rerank()

    def rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Reranks a list of documents based on a query.

        Args:
            query: The query string.
            documents: A list of documents to rerank.

        Returns:
            A list of reranked documents.
        """
        doc_texts = [doc["description"] for doc in documents]
        
        with Run().context(RunConfig(nranks=1, experiment="rerank")):
            reranked_indices = self.reranker.rerank(query, doc_texts)
        
        return [documents[i] for i in reranked_indices]