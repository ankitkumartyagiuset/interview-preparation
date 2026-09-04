import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.models import User, Resume, CandidateProfile, CandidateSkill, WorkExperience, Project, Certification
from app.schemas import (
    ResumeResponse, CandidateProfileResponse, CandidateProfileUpdate,
    SkillCategoryEnum, SkillLevelEnum
)
from app.security.auth import get_current_user, check_resource_access
from app.services.resume_parser import ResumeParser
from app.services.resume_analyzer import ResumeAnalyzer

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse resume"""

    # Validate file extension
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"
        )

    # Create storage directory
    user_storage_path = os.path.join(settings.STORAGE_PATH, f"user_{current_user.id}", "resumes")
    os.makedirs(user_storage_path, exist_ok=True)

    # Save file
    file_path = os.path.join(user_storage_path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Get file size
    file_size = os.path.getsize(file_path)

    # Validate file size
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
        )

    # Extract text
    try:
        resume_text = ResumeParser.extract_text(file_path, file_extension)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse resume: {str(e)}"
        )

    # Create resume record
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_extension,
        raw_text=resume_text,
        is_parsed=False
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Parse resume in background (for now, do it synchronously)
    try:
        analyzer = ResumeAnalyzer()
        profile_data = await analyzer.extract_structured_profile(resume_text)

        # Create candidate profile
        profile = CandidateProfile(
            resume_id=resume.id,
            full_name=profile_data.get('full_name'),
            email=profile_data.get('email'),
            phone=profile_data.get('phone'),
            location=profile_data.get('location'),
            summary=profile_data.get('summary'),
            total_experience_years=profile_data.get('total_experience_years'),
            education=profile_data.get('education', [])
        )
        db.add(profile)
        db.flush()

        # Add skills
        for skill_data in profile_data.get('skills', []):
            skill = CandidateSkill(
                profile_id=profile.id,
                skill_name=skill_data.get('name'),
                category=skill_data.get('category', 'other'),
                claimed_level=skill_data.get('level'),
                years_of_experience=skill_data.get('years')
            )
            db.add(skill)

        # Add experiences
        for exp_data in profile_data.get('experiences', []):
            experience = WorkExperience(
                profile_id=profile.id,
                company_name=exp_data.get('company'),
                job_title=exp_data.get('title'),
                start_date=exp_data.get('start_date'),
                end_date=exp_data.get('end_date'),
                is_current=exp_data.get('is_current', False),
                description=exp_data.get('description'),
                responsibilities=exp_data.get('responsibilities', [])
            )
            db.add(experience)

        # Add projects
        for proj_data in profile_data.get('projects', []):
            project = Project(
                profile_id=profile.id,
                project_name=proj_data.get('name'),
                description=proj_data.get('description'),
                technologies=proj_data.get('technologies', []),
                role=proj_data.get('role'),
                duration=proj_data.get('duration')
            )
            db.add(project)

        # Add certifications
        for cert_data in profile_data.get('certifications', []):
            certification = Certification(
                profile_id=profile.id,
                name=cert_data.get('name'),
                issuing_organization=cert_data.get('organization'),
                issue_date=cert_data.get('issue_date'),
                credential_id=cert_data.get('credential_id')
            )
            db.add(certification)

        resume.is_parsed = True
        db.commit()

    except Exception as e:
        print(f"Error parsing resume: {e}")
        # Don't fail the upload, just mark as not parsed
        db.commit()

    db.refresh(resume)
    return ResumeResponse.model_validate(resume)


@router.get("", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's resumes"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    return [ResumeResponse.model_validate(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resume details"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    check_resource_access(current_user, resume.user_id)
    return ResumeResponse.model_validate(resume)


@router.get("/{resume_id}/profile", response_model=CandidateProfileResponse)
async def get_resume_profile(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get parsed candidate profile"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    check_resource_access(current_user, resume.user_id)

    if not resume.profile:
        raise HTTPException(status_code=404, detail="Profile not yet parsed")

    return CandidateProfileResponse.model_validate(resume.profile)


@router.patch("/{resume_id}/profile", response_model=CandidateProfileResponse)
async def update_resume_profile(
    resume_id: int,
    profile_update: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update candidate profile"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    check_resource_access(current_user, resume.user_id)

    if not resume.profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update profile fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume.profile, field, value)

    db.commit()
    db.refresh(resume.profile)

    return CandidateProfileResponse.model_validate(resume.profile)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    check_resource_access(current_user, resume.user_id)

    # Delete file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.delete(resume)
    db.commit()

    return None
