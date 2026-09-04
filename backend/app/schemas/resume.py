from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class CandidateSkillSchema(BaseModel):
    id: Optional[int] = None
    skill_name: str
    category: Optional[str] = "technical"
    claimed_level: Optional[str] = "intermediate"  # 'beginner', 'intermediate', 'advanced', 'expert'
    years_of_exp: Optional[float] = 1.0
    context_evidence: Optional[str] = None

    class Config:
        from_attributes = True

class ProjectSchema(BaseModel):
    id: Optional[int] = None
    title: str
    role: Optional[str] = None
    description: Optional[str] = None
    tech_stack_json: Optional[List[str]] = []
    achievements_json: Optional[List[str]] = []
    url: Optional[str] = None

    class Config:
        from_attributes = True

class ExperienceSchema(BaseModel):
    id: Optional[int] = None
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = False
    responsibilities_json: Optional[List[str]] = []

    class Config:
        from_attributes = True

class CertificationSchema(BaseModel):
    id: Optional[int] = None
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None

    class Config:
        from_attributes = True

class CandidateProfileResponse(BaseModel):
    id: int
    resume_id: int
    user_id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    total_experience_years: float = 0.0
    education_json: List[Dict[str, Any]] = []
    skills: List[CandidateSkillSchema] = []
    projects: List[ProjectSchema] = []
    experiences: List[ExperienceSchema] = []
    certifications: List[CertificationSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    education_json: Optional[List[Dict[str, Any]]] = None
    skills: Optional[List[CandidateSkillSchema]] = None
    projects: Optional[List[ProjectSchema]] = None
    experiences: Optional[List[ExperienceSchema]] = None
    certifications: Optional[List[CertificationSchema]] = None

class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_size: int
    status: str
    created_at: datetime
    candidate_profile: Optional[CandidateProfileResponse] = None

    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    resume_id: int
    file_name: str
    status: str
    message: str
    profile: Optional[CandidateProfileResponse] = None
