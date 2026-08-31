from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AnswerEvaluationResponse(BaseModel):
    id: int
    answer_id: int
    score: float
    correctness: float
    technical_depth: float
    relevance: float
    clarity: float
    communication: float
    problem_solving: float
    strengths_json: List[str] = []
    weaknesses_json: List[str] = []
    evidence_json: List[str] = []
    demonstrated_skill_level: str
    feedback_summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
