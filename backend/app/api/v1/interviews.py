from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id_and_role
from backend.app.schemas.interview import (
    InterviewCreate,
    InterviewDetailResponse,
    InterviewStartResponse,
    AnswerSubmit,
    AnswerSubmitResponse
)
from backend.app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("", response_model=InterviewDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    data: InterviewCreate,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    interview_service = InterviewService(db)
    # Check if blueprint was supplied
    custom_blueprint = data.blueprint.model_dump() if data.blueprint else None
    
    return await interview_service.create_interview(
        user_id=user_info["user_id"],
        title=data.title,
        resume_id=data.resume_id,
        job_role_id=data.job_role_id,
        job_description_id=data.job_description_id,
        interview_type=data.interview_type or "mixed",
        difficulty=data.difficulty or "intermediate",
        total_questions=data.total_questions or 5,
        custom_blueprint=custom_blueprint
    )

@router.post("/{interview_id}/start", response_model=InterviewStartResponse)
async def start_interview(
    interview_id: int,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    interview_service = InterviewService(db)
    return await interview_service.start_interview(
        interview_id=interview_id,
        user_id=user_info["user_id"]
    )

@router.get("", response_model=List[InterviewDetailResponse])
def list_interviews(
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    interview_service = InterviewService(db)
    return interview_service.list_interviews(user_id=user_info["user_id"])

@router.get("/{interview_id}", response_model=InterviewDetailResponse)
def get_interview(
    interview_id: int,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    interview_service = InterviewService(db)
    return interview_service.get_interview(
        interview_id=interview_id,
        user_id=user_info["user_id"]
    )

@router.post("/{interview_id}/submit", response_model=AnswerSubmitResponse)
async def submit_answer(
    interview_id: int,
    data: AnswerSubmit,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    interview_service = InterviewService(db)
    return await interview_service.submit_answer(
        interview_id=interview_id,
        user_id=user_info["user_id"],
        question_id=data.question_id,
        answer_text=data.answer_text,
        time_taken_seconds=data.time_taken_seconds or 0
    )
