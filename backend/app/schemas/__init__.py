from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class UserRoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SkillCategoryEnum(str, Enum):
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    OTHER = "other"


class SkillLevelEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class InterviewStatusEnum(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewDifficultyEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class QuestionTypeEnum(str, Enum):
    TECHNICAL = "technical"
    PROJECT = "project"
    BEHAVIORAL = "behavioral"
    HR = "hr"
    PROBLEM_SOLVING = "problem_solving"
    ROLE_SPECIFIC = "role_specific"


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Resume schemas
class ResumeUpload(BaseModel):
    pass


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_size: Optional[int]
    file_type: Optional[str]
    is_parsed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Candidate Profile schemas
class SkillBase(BaseModel):
    skill_name: str
    category: SkillCategoryEnum = SkillCategoryEnum.OTHER
    claimed_level: Optional[SkillLevelEnum] = None
    years_of_experience: Optional[float] = None


class SkillResponse(SkillBase):
    id: int

    class Config:
        from_attributes = True


class WorkExperienceBase(BaseModel):
    company_name: str
    job_title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None


class WorkExperienceResponse(WorkExperienceBase):
    id: int

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    project_name: str
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    url: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class CertificationBase(BaseModel):
    name: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None


class CertificationResponse(CertificationBase):
    id: int

    class Config:
        from_attributes = True


class CandidateProfileBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    education: Optional[List[Dict[str, Any]]] = None


class CandidateProfileUpdate(CandidateProfileBase):
    pass


class CandidateProfileResponse(CandidateProfileBase):
    id: int
    resume_id: int
    skills: List[SkillResponse] = []
    experiences: List[WorkExperienceResponse] = []
    projects: List[ProjectResponse] = []
    certifications: List[CertificationResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Job Role schemas
class JobRoleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    required_skills: Optional[List[str]]
    preferred_skills: Optional[List[str]]
    responsibilities: Optional[List[str]]
    experience_level: Optional[str]

    class Config:
        from_attributes = True


# Job Description schemas
class JobDescriptionCreate(BaseModel):
    title: str
    company_name: Optional[str] = None
    raw_text: str


class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    company_name: Optional[str]
    required_skills: Optional[List[str]]
    preferred_skills: Optional[List[str]]
    experience_required: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Interview schemas
class InterviewCreate(BaseModel):
    resume_id: int
    job_role_id: Optional[int] = None
    job_description_id: Optional[int] = None
    difficulty: InterviewDifficultyEnum = InterviewDifficultyEnum.INTERMEDIATE


class InterviewResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_role_id: Optional[int]
    job_description_id: Optional[int]
    status: InterviewStatusEnum
    difficulty: InterviewDifficultyEnum
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    question_number: int
    question_type: QuestionTypeEnum
    question_text: str
    difficulty: Optional[str]
    skill_being_tested: Optional[str]
    is_followup: bool

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    answer_text: str = Field(..., min_length=1)


class AnswerEvaluationResponse(BaseModel):
    overall_score: float
    correctness_score: Optional[float]
    technical_depth_score: Optional[float]
    relevance_score: Optional[float]
    clarity_score: Optional[float]
    problem_solving_score: Optional[float]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    evidence: Optional[List[str]]
    skill_level_demonstrated: Optional[SkillLevelEnum]
    feedback: Optional[str]

    class Config:
        from_attributes = True


class SkillGapResponse(BaseModel):
    id: int
    skill_name: str
    required_level: Optional[SkillLevelEnum]
    claimed_level: Optional[SkillLevelEnum]
    demonstrated_level: Optional[SkillLevelEnum]
    gap_severity: Optional[str]
    priority: Optional[str]
    confidence: Optional[float]
    evidence: Optional[List[str]]

    class Config:
        from_attributes = True


class RoadmapItemResponse(BaseModel):
    id: int
    skill_name: str
    current_level: Optional[SkillLevelEnum]
    target_level: Optional[SkillLevelEnum]
    priority: Optional[str]
    day_number: Optional[int]
    concepts_to_learn: Optional[List[str]]
    practice_tasks: Optional[List[str]]
    mini_project: Optional[str]
    resources: Optional[List[Dict[str, str]]]

    class Config:
        from_attributes = True


class RoadmapResponse(BaseModel):
    id: int
    interview_id: int
    title: Optional[str]
    description: Optional[str]
    estimated_duration_days: Optional[int]
    items: List[RoadmapItemResponse] = []

    class Config:
        from_attributes = True


class InterviewReportResponse(BaseModel):
    id: int
    interview_id: int
    overall_score: float
    technical_score: Optional[float]
    project_score: Optional[float]
    problem_solving_score: Optional[float]
    communication_score: Optional[float]
    behavioral_score: Optional[float]
    readiness_percentage: Optional[float]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    key_findings: Optional[List[str]]
    recommendations: Optional[List[str]]
    summary: Optional[str]

    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardResponse(BaseModel):
    user: UserResponse
    total_interviews: int
    completed_interviews: int
    average_score: Optional[float]
    readiness_percentage: Optional[float]
    recent_interviews: List[InterviewResponse]
    top_strengths: List[str]
    priority_gaps: List[str]


class ProgressResponse(BaseModel):
    interview_history: List[Dict[str, Any]]
    score_trend: List[Dict[str, Any]]
    skill_improvement: Dict[str, Any]
