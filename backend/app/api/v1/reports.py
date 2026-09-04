from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id_and_role
from app.schemas.report import ReportResponse
from app.schemas.roadmap import RoadmapResponse, RoadmapItemResponse
from app.schemas.skill_gap import SkillGapResponse
from app.repositories.report_repo import ReportRepository

router = APIRouter(prefix="/reports", tags=["Reports & Roadmaps"])

@router.get("/{interview_id}", response_model=ReportResponse)
def get_report(
    interview_id: int,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    report_repo = ReportRepository(db)
    report = report_repo.get_report_by_interview(interview_id, user_id=user_info["user_id"])
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this interview session. Make sure it is completed first."
        )
    
    # Enrich report response with skill gaps and roadmap
    report.skill_gaps = report_repo.get_skill_gaps_by_interview(interview_id)
    report.roadmap = report_repo.get_roadmap_by_interview(interview_id)
    return report

@router.get("/{interview_id}/roadmap", response_model=RoadmapResponse)
def get_roadmap(
    interview_id: int,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    report_repo = ReportRepository(db)
    roadmap = report_repo.get_roadmap_by_interview(interview_id)
    if not roadmap or roadmap.user_id != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found for this interview session."
        )
    return roadmap

@router.get("/{interview_id}/gaps", response_model=List[SkillGapResponse])
def get_skill_gaps(
    interview_id: int,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    report_repo = ReportRepository(db)
    # Check if report exists to authorize
    report = report_repo.get_report_by_interview(interview_id, user_id=user_info["user_id"])
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report/Skill gaps not found for this interview session."
        )
    return report_repo.get_skill_gaps_by_interview(interview_id)

@router.put("/roadmap/items/{item_id}/toggle", response_model=RoadmapItemResponse)
def toggle_roadmap_item(
    item_id: int,
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    report_repo = ReportRepository(db)
    item = report_repo.toggle_roadmap_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap item not found."
        )
    return item
