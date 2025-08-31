from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    """
    Represents a single task from the BIRD dataset.
    """
    question_id: int
    db_id: str
    question: str
    evidence: Optional[str] = None
    SQL: Optional[str] = None
    difficulty: Optional[str] = None