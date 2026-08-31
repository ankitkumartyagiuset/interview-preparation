from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ProgressTrendItem(BaseModel):
    interview_id: int
    interview_title: str
    date: str
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float

class DashboardSummaryResponse(BaseModel):
    user_name: str
    total_interviews: int
    completed_interviews: int
    overall_readiness: float
    readiness_band: str
    category_averages: Dict[str, float]  # {'technical': 82.0, 'projects': 76.0, ...}
    top_strengths: List[str]
    priority_gaps: List[Dict[str, Any]]
    recent_interviews: List[Dict[str, Any]]
    progress_trend: List[ProgressTrendItem]
    active_roadmap: Optional[Dict[str, Any]] = None
