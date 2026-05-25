from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Question:
    question_text: str
    choices: Dict[str, str]
    correct_answer: str
    rationale: str

@dataclass
class QuizSession:
    set_name: str
    part_name: str
    questions: List[Question]
    current_index: int = 0
    score: int = 0
    completed: bool = False
    user_answers: Dict[int, str] = field(default_factory=dict)