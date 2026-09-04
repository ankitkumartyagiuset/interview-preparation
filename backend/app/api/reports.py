from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import (
    User, Interview, InterviewReport, SkillGap, Roadmap,
    InterviewQuestion, InterviewAnswer
)
from app.schemas import (
    InterviewReportResponse, SkillGapResponse, RoadmapResponse
)
from app.security.auth import get_current_user, check_resource_access
from app.services.skill_gap_analyzer import SkillGapAnalyzer, RoadmapGenerator
from app.services.report_generator import ReportGenerator

router = APIRouter(prefix="/interviews", tags=["reports"])


@router.get("/{interview_id}/report", response_model=InterviewReportResponse)
async def get_interview_report(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interview report"""

    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    check_resource_access(current_user, interview.user_id)

    # Check if report exists
    if interview.report:
        return InterviewReportResponse.model_validate(interview.report)

    # Generate report if interview is completed
    if interview.status.value != "completed":
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    # Get questions and evaluations
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview.id
    ).order_by(InterviewQuestion.question_number).all()

    evaluations = []
    for q in questions:
        if q.answer and q.answer.evaluation:
            evaluations.append({
                'overall_score': q.answer.evaluation.overall_score,
                'correctness_score': q.answer.evaluation.correctness_score,
                'technical_depth_score': q.answer.evaluation.technical_depth_score,
                'relevance_score': q.answer.evaluation.relevance_score,
                'clarity_score': q.answer.evaluation.clarity_score,
                'problem_solving_score': q.answer.evaluation.problem_solving_score,
                'strengths': q.answer.evaluation.strengths,
                'weaknesses': q.answer.evaluation.weaknesses
            })

    # Get skill gaps
    skill_gaps = db.query(SkillGap).filter(SkillGap.interview_id == interview.id).all()
    skill_gaps_data = [{
        'skill': sg.skill_name,
        'gap_severity': sg.gap_severity,
        'priority': sg.priority
    } for sg in skill_gaps]

    # Generate report
    generator = ReportGenerator()
    job_profile = _build_job_profile(interview)

    try:
        report_data = await generator.generate_interview_report(
            interview_data={
                'job_title': job_profile.get('title'),
                'difficulty': interview.difficulty.value,
                'questions': [{'type': q.question_type.value} for q in questions]
            },
            evaluations=evaluations,
            skill_gaps=skill_gaps_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

    # Save report
    report = InterviewReport(
        interview_id=interview.id,
        overall_score=report_data.get('overall_score', 0),
        technical_score=report_data.get('technical_score'),
        project_score=report_data.get('project_score'),
        problem_solving_score=report_data.get('problem_solving_score'),
        communication_score=report_data.get('communication_score'),
        behavioral_score=report_data.get('behavioral_score'),
        readiness_percentage=report_data.get('readiness_percentage'),
        strengths=report_data.get('strengths', []),
        weaknesses=report_data.get('weaknesses', []),
        key_findings=report_data.get('key_findings', []),
        recommendations=report_data.get('recommendations', []),
        summary=report_data.get('summary')
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return InterviewReportResponse.model_validate(report)


@router.get("/{interview_id}/skill-gaps", response_model=list[SkillGapResponse])
async def get_skill_gaps(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skill gap analysis"""

    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    check_resource_access(current_user, interview.user_id)

    # Check if skill gaps exist
    existing_gaps = db.query(SkillGap).filter(SkillGap.interview_id == interview.id).all()
    if existing_gaps:
        return [SkillGapResponse.model_validate(sg) for sg in existing_gaps]

    # Generate skill gaps if interview is completed
    if interview.status.value != "completed":
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    # Get profile skills
    profile = interview.resume.profile
    profile_skills = [{
        'name': s.skill_name,
        'category': s.category.value,
        'claimed_level': s.claimed_level.value if s.claimed_level else None,
        'years': s.years_of_experience
    } for s in profile.skills]

    # Get job requirements
    job_profile = _build_job_profile(interview)

    # Get questions and evaluations
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview.id
    ).order_by(InterviewQuestion.question_number).all()

    evaluations = []
    for q in questions:
        if q.answer and q.answer.evaluation:
            evaluations.append({
                'overall_score': q.answer.evaluation.overall_score,
                'skill_level_demonstrated': q.answer.evaluation.skill_level_demonstrated.value if q.answer.evaluation.skill_level_demonstrated else None
            })

    # Analyze skill gaps
    analyzer = SkillGapAnalyzer()
    try:
        gaps_data = await analyzer.analyze_skill_gaps(
            profile_skills=profile_skills,
            job_requirements=job_profile,
            interview_evaluations=evaluations,
            questions=[{'skill': q.skill_being_tested, 'type': q.question_type.value} for q in questions]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze skill gaps: {str(e)}")

    # Save skill gaps
    for gap_data in gaps_data:
        skill_gap = SkillGap(
            interview_id=interview.id,
            skill_name=gap_data.get('skill'),
            required_level=gap_data.get('required_level'),
            claimed_level=gap_data.get('claimed_level'),
            demonstrated_level=gap_data.get('demonstrated_level'),
            gap_severity=gap_data.get('gap_severity'),
            priority=gap_data.get('priority'),
            confidence=gap_data.get('confidence'),
            evidence=gap_data.get('evidence', [])
        )
        db.add(skill_gap)

    db.commit()

    # Reload and return
    skill_gaps = db.query(SkillGap).filter(SkillGap.interview_id == interview.id).all()
    return [SkillGapResponse.model_validate(sg) for sg in skill_gaps]


@router.get("/{interview_id}/roadmap", response_model=RoadmapResponse)
async def get_roadmap(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get improvement roadmap"""

    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    check_resource_access(current_user, interview.user_id)

    # Check if roadmap exists
    if interview.roadmap:
        return RoadmapResponse.model_validate(interview.roadmap)

    # Generate roadmap if interview is completed
    if interview.status.value != "completed":
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    # Get skill gaps
    skill_gaps = db.query(SkillGap).filter(SkillGap.interview_id == interview.id).all()
    if not skill_gaps:
        # Generate skill gaps first
        await get_skill_gaps(interview_id, current_user, db)
        skill_gaps = db.query(SkillGap).filter(SkillGap.interview_id == interview.id).all()

    skill_gaps_data = [{
        'skill': sg.skill_name,
        'required_level': sg.required_level.value if sg.required_level else None,
        'claimed_level': sg.claimed_level.value if sg.claimed_level else None,
        'demonstrated_level': sg.demonstrated_level.value if sg.demonstrated_level else None,
        'gap_severity': sg.gap_severity,
        'priority': sg.priority
    } for sg in skill_gaps]

    # Generate roadmap
    generator = RoadmapGenerator()
    profile_data = {
        'total_experience_years': interview.resume.profile.total_experience_years
    }

    try:
        roadmap_data = await generator.generate_roadmap(
            skill_gaps=skill_gaps_data,
            profile_data=profile_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate roadmap: {str(e)}")

    # Save roadmap
    from app.models import Roadmap, RoadmapItem

    roadmap = Roadmap(
        interview_id=interview.id,
        title=roadmap_data.get('title'),
        description=roadmap_data.get('description'),
        estimated_duration_days=roadmap_data.get('estimated_duration_days')
    )
    db.add(roadmap)
    db.flush()

    for item_data in roadmap_data.get('items', []):
        roadmap_item = RoadmapItem(
            roadmap_id=roadmap.id,
            skill_name=item_data.get('skill'),
            current_level=item_data.get('current_level'),
            target_level=item_data.get('target_level'),
            priority=item_data.get('priority'),
            day_number=item_data.get('day_number'),
            concepts_to_learn=item_data.get('concepts_to_learn', []),
            practice_tasks=item_data.get('practice_tasks', []),
            mini_project=item_data.get('mini_project'),
            resources=item_data.get('resources', [])
        )
        db.add(roadmap_item)

    db.commit()
    db.refresh(roadmap)

    return RoadmapResponse.model_validate(roadmap)


def _build_job_profile(interview):
    """Build job profile from interview"""
    if interview.job_role:
        return {
            'title': interview.job_role.title,
            'required_skills': interview.job_role.required_skills or [],
            'preferred_skills': interview.job_role.preferred_skills or []
        }
    elif interview.job_description:
        return {
            'title': interview.job_description.title,
            'required_skills': interview.job_description.required_skills or [],
            'preferred_skills': interview.job_description.preferred_skills or []
        }
    return {'title': 'Unknown', 'required_skills': [], 'preferred_skills': []}
