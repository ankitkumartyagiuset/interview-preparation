from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class BlueprintConfig(BaseModel):
    technical_weight: int = 30
    project_weight: int = 20
    problem_solving_weight: int = 20
    communication_weight: int = 10
    behavioral_weight: int = 10
    role_specific_weight: int = 10
    target_skills: Optional[List[str]] = []

class InterviewCreate(BaseModel):
    resume_id: Optional[int] = None
    job_role_id: Optional[int] = None
    job_description_id: Optional[int] = None
    title: Optional[str] = None
    interview_type: Optional[str] = "mixed"  # 'technical', 'project', 'behavioral', 'hr', 'mixed', 'role_specific'
    difficulty: Optional[str] = "intermediate"  # 'beginner', 'intermediate', 'advanced', 'expert'
    total_questions: Optional[int] = 5
    blueprint: Optional[BlueprintConfig] = None

from backend.app.schemas.evaluation import AnswerEvaluationResponse

class AnswerResponse(BaseModel):
    id: int
    answer_text: str
    time_taken_seconds: int
    evaluation: Optional[AnswerEvaluationResponse] = None

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int
    sequence_num: int
    category: str
    target_skill: Optional[str] = None
    difficulty: str
    question_text: str
    is_follow_up: bool = False
    parent_question_id: Optional[int] = None
    answer: Optional[AnswerResponse] = None

    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str = Field(..., min_length=2)
    time_taken_seconds: Optional[int] = 0

class AnswerSubmitResponse(BaseModel):
    evaluation_id: Optional[int] = None
    feedback_summary: Optional[str] = None
    next_question: Optional[QuestionResponse] = None
    is_finished: bool = False
    current_question_index: int
    total_questions: int

class InterviewDetailResponse(BaseModel):
    id: int
    user_id: int
    resume_id: Optional[int] = None
    job_role_id: Optional[int] = None
    job_description_id: Optional[int] = None
    title: str
    interview_type: str
    difficulty: str
    status: str
    current_question_index: int
    total_questions: int
    overall_score: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True

class InterviewStartResponse(BaseModel):
    interview_id: int
    title: str
    total_questions: int
    first_question: QuestionResponse
    status: str
