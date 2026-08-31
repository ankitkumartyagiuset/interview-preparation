from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class SkillGapResponse(BaseModel):
    id: int
    interview_id: int
    skill_name: str
    category: str
    required_level: str
    claimed_level: str
    demonstrated_level: str
    gap_severity: str
    priority: str
    confidence_score: float
    evidence_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
