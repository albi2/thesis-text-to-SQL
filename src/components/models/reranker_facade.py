from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModel

class Reranker:
    def __init__(
        self,
        model: str = "colbert-ir/colbertv2.0",
        tokenizer: str = "colbert-ir/colbertv2.0",
    ):
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self._model = AutoModel.from_pretrained(model)

    def _calculate_sim(self, query: str, documents_text_list: List[str]) -> List[float]:
        query_encoding = self._tokenizer(query, return_tensors="pt")
        query_embedding = self._model(**query_encoding).last_hidden_state
        rerank_score_list = []

        for document_text in documents_text_list:
            document_encoding = self._tokenizer(
                document_text, return_tensors="pt", truncation=True, max_length=512
            )
            document_embedding = self._model(**document_encoding).last_hidden_state

            sim_matrix = torch.nn.functional.cosine_similarity(
                query_embedding.unsqueeze(2), document_embedding.unsqueeze(1), dim=-1
            )
            
            max_sim_scores, _ = torch.max(sim_matrix, dim=2)
            rerank_score_list.append(torch.mean(max_sim_scores, dim=1).item())

        return rerank_score_list

    def rerank(self, query: str, documents: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
        """
        Reranks a list of documents based on a query using a custom Colbert implementation.

        Args:
            query: The query string.
            documents: A list of documents to rerank. Each document is a dictionary.
            k: The number of documents to return.

        Returns:
            A list of reranked documents.
        """
        if not documents:
            return []

        doc_texts = [doc["description"] for doc in documents]
        
        scores = self._calculate_sim(query, doc_texts)
        
        scored_documents = list(zip(documents, scores))
        
        scored_documents.sort(key=lambda x: x[1], reverse=True)
        
        reranked_documents = [doc for doc, score in scored_documents]
        
        return reranked_documents[:k]