from src.database import DatabaseManager
from typing import Optional, Dict, Any

class ScoreManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def save_score(self, set_name: str, part_name: str, score: int, total: int):
        percentage = (score / total) * 100 if total > 0 else 0
        with self.db.get_connection() as conn:
            conn.execute('''
                INSERT INTO scores (set_name, part_name, score, total_questions, percentage)
                VALUES (?, ?, ?, ?, ?)
            ''', (set_name, part_name, score, total, percentage))
            conn.commit()

    def get_previous_score(self, set_name: str, part_name: str) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT score, total_questions, percentage 
                FROM scores 
                WHERE set_name = ? AND part_name = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (set_name, part_name))
            row = cursor.fetchone()
            return dict(row) if row else None