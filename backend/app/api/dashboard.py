from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any
from app.core.database import get_db
from app.models import User, Interview, InterviewStatus, InterviewReport
from app.schemas import DashboardResponse, ProgressResponse, InterviewResponse, UserResponse
from app.security.auth import get_current_user

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard data"""

    # Get interview stats
    total_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).count()

    completed_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == InterviewStatus.COMPLETED
    ).count()

    # Get average score
    avg_score_result = db.query(func.avg(InterviewReport.overall_score)).join(
        Interview
    ).filter(
        Interview.user_id == current_user.id
    ).scalar()

    average_score = float(avg_score_result) if avg_score_result else None

    # Get average readiness
    avg_readiness = db.query(func.avg(InterviewReport.readiness_percentage)).join(
        Interview
    ).filter(
        Interview.user_id == current_user.id
    ).scalar()

    readiness_percentage = float(avg_readiness) if avg_readiness else None

    # Get recent interviews
    recent_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(desc(Interview.created_at)).limit(5).all()

    # Get top strengths (from recent completed interviews)
    strengths_list = []
    weaknesses_list = []

    completed = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == InterviewStatus.COMPLETED
    ).order_by(desc(Interview.created_at)).limit(3).all()

    for interview in completed:
        if interview.report:
            strengths_list.extend(interview.report.strengths or [])
            weaknesses_list.extend(interview.report.weaknesses or [])

    # Get unique top strengths and weaknesses
    top_strengths = list(set(strengths_list))[:5]
    priority_gaps = list(set(weaknesses_list))[:5]

    return DashboardResponse(
        user=UserResponse.model_validate(current_user),
        total_interviews=total_interviews,
        completed_interviews=completed_interviews,
        average_score=average_score,
        readiness_percentage=readiness_percentage,
        recent_interviews=[InterviewResponse.model_validate(i) for i in recent_interviews],
        top_strengths=top_strengths,
        priority_gaps=priority_gaps
    )


@router.get("/progress", response_model=ProgressResponse)
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user progress tracking"""

    # Get interview history with scores
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == InterviewStatus.COMPLETED
    ).order_by(Interview.completed_at).all()

    interview_history = []
    score_trend = []

    for interview in interviews:
        history_item = {
            'interview_id': interview.id,
            'date': interview.completed_at.isoformat() if interview.completed_at else None,
            'role': interview.job_role.title if interview.job_role else (
                interview.job_description.title if interview.job_description else 'Unknown'
            ),
            'score': interview.report.overall_score if interview.report else None,
            'readiness': interview.report.readiness_percentage if interview.report else None
        }
        interview_history.append(history_item)

        if interview.report:
            score_trend.append({
                'date': interview.completed_at.isoformat() if interview.completed_at else None,
                'overall_score': interview.report.overall_score,
                'technical_score': interview.report.technical_score,
                'readiness_percentage': interview.report.readiness_percentage
            })

    # Build skill improvement tracking
    skill_improvement = {
        'note': 'Track skill improvements across multiple interviews',
        'trends': []
    }

    return ProgressResponse(
        interview_history=interview_history,
        score_trend=score_trend,
        skill_improvement=skill_improvement
    )


@router.get("/history", response_model=list[InterviewResponse])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interview history"""

    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(desc(Interview.created_at)).all()

    return [InterviewResponse.model_validate(i) for i in interviews]
