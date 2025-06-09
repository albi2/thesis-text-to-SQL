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