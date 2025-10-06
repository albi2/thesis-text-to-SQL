import pickle
from langchain.retrievers import BM25Retriever

class BM25Util:
    @staticmethod
    def load_bm25_retriever(db_id: str) -> BM25Retriever:
        """
        Loads the BM25 retriever for a given database.

        Args:
            db_id: The ID of the database.

        Returns:
            The loaded BM25Retriever object.
        """
        bm25_path = f"/var/tmp/ge62nok/bm25/{db_id}_bm25_retriever.pkl"
        with open(bm25_path, "rb") as f:
            bm25_retriever = pickle.load(f)
        return bm25_retriever