from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import User, JobRole, JobDescription
from app.schemas import JobRoleResponse, JobDescriptionCreate, JobDescriptionResponse
from app.security.auth import get_current_user
from app.services.job_analyzer import JobDescriptionAnalyzer

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/roles", response_model=List[JobRoleResponse])
async def list_job_roles(db: Session = Depends(get_db)):
    """List available job roles"""
    roles = db.query(JobRole).order_by(JobRole.title).all()
    return [JobRoleResponse.model_validate(r) for r in roles]


@router.get("/roles/{role_id}", response_model=JobRoleResponse)
async def get_job_role(role_id: int, db: Session = Depends(get_db)):
    """Get job role details"""
    role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Job role not found")
    return JobRoleResponse.model_validate(role)


@router.post("/descriptions", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    jd_data: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and analyze job description"""

    # Analyze JD
    analyzer = JobDescriptionAnalyzer()
    try:
        analysis = await analyzer.analyze_job_description(jd_data.raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze job description: {str(e)}"
        )

    # Create JD record
    jd = JobDescription(
        user_id=current_user.id,
        title=jd_data.title or analysis.get('title', 'Untitled Position'),
        company_name=jd_data.company_name,
        raw_text=jd_data.raw_text,
        parsed_data=analysis,
        required_skills=analysis.get('required_skills', []),
        preferred_skills=analysis.get('preferred_skills', []),
        experience_required=analysis.get('experience_level')
    )

    db.add(jd)
    db.commit()
    db.refresh(jd)

    return JobDescriptionResponse.model_validate(jd)


@router.get("/descriptions", response_model=List[JobDescriptionResponse])
async def list_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's job descriptions"""
    jds = db.query(JobDescription).filter(
        JobDescription.user_id == current_user.id
    ).order_by(JobDescription.created_at.desc()).all()
    return [JobDescriptionResponse.model_validate(jd) for jd in jds]


@router.get("/descriptions/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    jd_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job description details"""
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    if jd.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return JobDescriptionResponse.model_validate(jd)
