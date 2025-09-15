"""
This module defines the LSHUtil class for Local-Sensitivity Hashing.
"""

import pickle
from typing import List, Dict, Any
from datasketch import MinHash, MinHashLSH

class LSHUtil:
    """
    Utility class for Local-Sensitivity Hashing.
    
    This class is intended to provide methods for performing LSH on data.
    Future implementation will include specific LSH algorithms and functionalities.
    """
    def __init__(self):
        """
        Initializes the LSHUtil class.
        """
        # TODO: Implement Local-Sensitivity Hashing functionality.
        pass

    @staticmethod
    def create_minhash(value: str, num_perm: int = 128, n_gram_size: int = 3) -> MinHash:
        """
        Creates a MinHash for a given string value.

        Args:
            value: The string value to be hashed.
            num_perm: The number of permutation functions to use.
            n_gram_size: The size of n-grams to use for shingling.

        Returns:
            A MinHash object.
        """
        minhash = MinHash(num_perm=num_perm)
        for i in range(len(value) - n_gram_size + 1):
            minhash.update(value[i:i+n_gram_size].encode('utf8'))
        return minhash

    @staticmethod
    def load_lsh_index(db_id: str) -> MinHashLSH:
        """
        Loads the LSH index from a pickle file.

        Args:
            db_id: The ID of the database.

        Returns:
            A MinHashLSH object.
        """
        lsh_path = f"dataset/lsh/{db_id}_lsh.pkl"
        with open(lsh_path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def load_minhashes(db_id: str) -> Dict[str, Any]:
        """
        Loads the MinHash mappings from a pickle file.

        Args:
            db_id: The ID of the database.

        Returns:
            A dictionary containing the MinHash mappings.
        """
        minhashes_path = f"dataset/lsh/{db_id}_minhashes.pkl"
        with open(minhashes_path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def query_lsh(lsh: MinHashLSH, minhashes: Dict[str, Any], query: str, top_n: int = 100, num_perm: int = 128, n_gram_size: int = 3) -> Dict[str, Dict[str, List[str]]]:
        """
        Queries the LSH index for similar values.

        Args:
            lsh: The LSH index.
            minhashes: The MinHash mappings.
            query: The query string.
            top_n: The number of top results to return.
            num_perm: The number of permutation functions to use.
            n_gram_size: The size of n-grams to use for shingling.

        Returns:
            A dictionary containing the top-n similar values, grouped by table and column.
        """
        query_minhash = LSHUtil.create_minhash(query, num_perm=num_perm, n_gram_size=n_gram_size)
        result = lsh.query(query_minhash)
        
        # Calculate Jaccard similarity and sort results
        results_with_similarity = []
        for key in result:
            similarity = query_minhash.jaccard(minhashes[key]["minhash"])
            results_with_similarity.append({
                "key": key,
                "similarity": similarity,
                "value": minhashes[key]["value"],
                "table_name": minhashes[key]["table_name"],
                "column_name": minhashes[key]["column_name"]
            })
            
        results_with_similarity.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Group results by table and column
        grouped_results = {}
        for res in results_with_similarity[:top_n]:
            table_name = res["table_name"]
            column_name = res["column_name"]
            if table_name not in grouped_results:
                grouped_results[table_name] = {}
            if column_name not in grouped_results[table_name]:
                grouped_results[table_name][column_name] = []
            grouped_results[table_name][column_name].append(res["value"])
            
        return grouped_results

    @staticmethod
    def _jaccard(m1: MinHash, m2: MinHash) -> float:
        """
        Calculates the Jaccard similarity between two MinHashes.

        Args:
            m1: The first MinHash.
            m2: The second MinHash.

        Returns:
            The Jaccard similarity.
        """
        return m1.jaccard(m2)