from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class RoadmapItemResponse(BaseModel):
    id: int
    day_number: int
    skill_name: str
    current_level: str
    target_level: str
    priority: str
    concepts_json: List[str] = []
    practice_tasks_json: List[str] = []
    mini_project_json: Dict[str, Any] = {}
    sample_questions_json: List[str] = []
    is_completed: bool = False

    class Config:
        from_attributes = True

class RoadmapResponse(BaseModel):
    id: int
    interview_id: int
    user_id: int
    title: str
    duration_days: int
    summary: Optional[str] = None
    overall_recommendation: Optional[str] = None
    created_at: datetime
    items: List[RoadmapItemResponse] = []

    class Config:
        from_attributes = True
