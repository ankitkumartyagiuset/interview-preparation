from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id_and_role
from backend.app.schemas.job import (
    JobRoleResponse,
    JobDescriptionResponse,
    JobDescriptionCreate,
    JobMatchAnalysis
)
from backend.app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs & Job Descriptions"])

@router.get("/roles", response_model=List[JobRoleResponse])
def get_job_roles(db: Session = Depends(get_db)):
    job_service = JobService(db)
    return job_service.list_roles()

@router.get("/roles/{role_id}", response_model=JobRoleResponse)
def get_job_role(role_id: int, db: Session = Depends(get_db)):
    job_service = JobService(db)
    return job_service.get_role(role_id)

@router.post("/descriptions", response_model=JobDescriptionResponse)
async def create_job_description(
    data: JobDescriptionCreate,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    job_service = JobService(db)
    return await job_service.create_job_description(
        user_id=user_info["user_id"],
        title=data.title,
        company=data.company,
        raw_text=data.raw_text,
        seniority=data.seniority or "intermediate"
    )

@router.get("/match", response_model=JobMatchAnalysis)
def match_resume_with_job(
    resume_id: int,
    job_role_id: Optional[int] = None,
    job_description_id: Optional[int] = None,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    if not job_role_id and not job_description_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either job_role_id or job_description_id must be provided for matching."
        )
    job_service = JobService(db)
    return job_service.match_resume_with_role(
        resume_id=resume_id,
        user_id=user_info["user_id"],
        job_role_id=job_role_id,
        job_description_id=job_description_id
    )
