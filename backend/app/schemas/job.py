from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class JobRoleCreate(BaseModel):
    title: str
    department: Optional[str] = None
    seniority: Optional[str] = "intermediate"
    description: Optional[str] = None
    core_skills_json: Optional[List[Dict[str, Any]]] = []
    default_blueprint_json: Optional[Dict[str, Any]] = None

class JobRoleResponse(BaseModel):
    id: int
    title: str
    department: Optional[str] = None
    seniority: str
    description: Optional[str] = None
    core_skills_json: List[Dict[str, Any]] = []
    default_blueprint_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class JobDescriptionCreate(BaseModel):
    title: str
    company: Optional[str] = None
    raw_text: str = Field(..., min_length=20)
    seniority: Optional[str] = "intermediate"

class JobDescriptionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    company: Optional[str] = None
    raw_text: str
    required_skills_json: List[Dict[str, Any]] = []
    preferred_skills_json: List[Dict[str, Any]] = []
    responsibilities_json: List[str] = []
    seniority: str
    experience_years_required: float
    created_at: datetime

    class Config:
        from_attributes = True

class JobMatchAnalysis(BaseModel):
    match_score: float  # 0 to 100
    matched_skills: List[Dict[str, Any]] = []
    missing_skills: List[Dict[str, Any]] = []
    weak_skills: List[Dict[str, Any]] = []
    relevant_projects: List[str] = []
    recommended_topics: List[str] = []
    readiness_label: str  # "Interview Ready", "Developing", etc.
