from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.skill_gap import SkillGapResponse
from backend.app.schemas.roadmap import RoadmapResponse

class ReportResponse(BaseModel):
    id: int
    interview_id: int
    user_id: int
    overall_readiness_score: float
    readiness_band: str
    technical_score: float
    project_score: float
    problem_solving_score: float
    communication_score: float
    hr_score: float
    role_specific_score: float
    strengths_json: List[str] = []
    weaknesses_json: List[str] = []
    verified_claims_json: List[Dict[str, Any]] = []
    summary: Optional[str] = None
    recommendation: Optional[str] = None
    disclaimer: str
    created_at: datetime
    
    # Nested relations when retrieved with details
    skill_gaps: Optional[List[SkillGapResponse]] = []
    roadmap: Optional[RoadmapResponse] = None

    class Config:
        from_attributes = True
