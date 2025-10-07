"""
This module defines the EditDistanceUtil class for calculating edit distance
between two strings.
"""
import Levenshtein

class EditDistanceUtil:
    """
    Utility class for calculating edit distance (Levenshtein distance)
    between two text strings.
    """
    def __init__(self):
        """
        Initializes the EditDistanceUtil class.
        """
        pass

    def calculate_distance(self, text1: str, text2: str) -> int:
        """
        Calculates the Levenshtein distance between two strings.

        Args:
            text1 (str): The first string.
            text2 (str): The second string.

        Returns:
            int: The Levenshtein distance between text1 and text2.
                 Returns 0 if both strings are identical or both are None/empty.
                 Returns length of the non-empty string if one is empty/None.
        """
        if text1 is None and text2 is None:
            return 0
        if text1 is None:
            return len(text2) if text2 else 0
        if text2 is None:
            return len(text1) if text1 else 0
            
        return Levenshtein.distance(text1, text2)

    @staticmethod
    def get_top_n_similar(query: str, candidates: list, top_n: int = 10) -> list:
        """
        Calculates the edit distance for all candidates and returns the top N.

        Args:
            query (str): The query string.
            candidates (list): A list of candidate dictionaries. Each dictionary must have a "value" key.
            top_n (int): The number of top candidates to return.

        Returns:
            list: A sorted list of the top N candidates with an added 'distance' key.
        """
        if not candidates:
            return []

        for candidate in candidates:
            candidate['distance'] = Levenshtein.distance(query, candidate['value'])

        candidates.sort(key=lambda x: x['distance'])

        return candidates[:top_n]

    @staticmethod
    def get_similar_by_threshold(query: str, candidates: list, threshold: float = 0.3) -> list:
        """
        Gets candidates with a normalized edit similarity above a certain threshold.

        Args:
            query (str): The query string.
            candidates (list): A list of candidate dictionaries. Each dictionary must have a "value" key.
            threshold (float): The minimum similarity threshold.

        Returns:
            list: A list of candidates with their 'edit_similarity' score, exceeding the threshold.
        """
        if not candidates:
            return []

        results = []
        for candidate in candidates:
            distance = Levenshtein.distance(query, candidate['value'])
            max_len = max(len(query), len(candidate['value']))
            similarity = 1 - (distance / max_len) if max_len > 0 else 0
            if similarity >= threshold:
                candidate['distance'] = similarity
                results.append(candidate)
        
        results.sort(key=lambda x: x['distance'], reverse=True)
        return results