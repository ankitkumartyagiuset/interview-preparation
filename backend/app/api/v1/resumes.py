from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id_and_role
from app.schemas.resume import (
    ResumeResponse,
    ResumeUploadResponse,
    CandidateProfileResponse,
    CandidateProfileUpdate
)
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    provider: Optional[str] = Form(None),
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    resume_service = ResumeService(db)
    return await resume_service.upload_and_process_resume(
        user_id=user_info["user_id"],
        file=file,
        provider_name=provider
    )

@router.get("", response_model=List[ResumeResponse])
def list_resumes(
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    resume_service = ResumeService(db)
    return resume_service.list_resumes(user_info["user_id"])

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    resume_service = ResumeService(db)
    return resume_service.get_resume(resume_id, user_info["user_id"])

@router.put("/{resume_id}/profile", response_model=CandidateProfileResponse)
def update_resume_profile(
    resume_id: int,
    update_data: CandidateProfileUpdate,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    resume_service = ResumeService(db)
    return resume_service.update_profile(
        resume_id=resume_id,
        user_id=user_info["user_id"],
        update_data=update_data.model_dump(exclude_unset=True)
    )

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    resume_service = ResumeService(db)
    resume_service.delete_resume(resume_id, user_info["user_id"])
    return {"message": "Resume deleted successfully."}
