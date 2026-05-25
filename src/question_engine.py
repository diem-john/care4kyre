import json
import random
from typing import Dict, List
from src.models import Question

class QuestionBank:
    def __init__(self, json_path: str = "data/question_bank.json"):
        self.json_path = json_path
        self._data = self._load_data()

    def _load_data(self) -> dict:
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def get_available_sets(self) -> List[str]:
        return list(self._data.keys())

    def get_parts_for_set(self, set_name: str) -> List[str]:
        return list(self._data.get(set_name, {}).keys())

    def get_shuffled_questions(self, set_name: str, part_name: str) -> List[Question]:
        raw_questions = self._data.get(set_name, {}).get(part_name, [])
        questions = [
            Question(
                question_text=q["question"],
                choices=q["choices"],
                correct_answer=q["correct_answer"],
                rationale=q["rationale"]
            )
            for q in raw_questions
        ]
        random.shuffle(questions)
        return questions