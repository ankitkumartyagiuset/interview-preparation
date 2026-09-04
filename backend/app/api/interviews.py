from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from app.core.database import get_db
from app.models import (
    User, Interview, InterviewStatus, Resume, JobRole, JobDescription,
    InterviewQuestion, InterviewAnswer, AnswerEvaluation, QuestionType
)
from app.schemas import (
    InterviewCreate, InterviewResponse, QuestionResponse,
    AnswerSubmit, AnswerEvaluationResponse, SkillGapResponse,
    RoadmapResponse, InterviewReportResponse
)
from app.security.auth import get_current_user, check_resource_access
from app.services.interview_engine import InterviewPlanner, QuestionGenerator
from app.services.answer_evaluator import AnswerEvaluator, FollowUpGenerator
from app.services.skill_gap_analyzer import SkillGapAnalyzer, RoadmapGenerator
from app.services.report_generator import ReportGenerator

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new interview"""

    # Verify resume exists and belongs to user
    resume = db.query(Resume).filter(Resume.id == interview_data.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    check_resource_access(current_user, resume.user_id)

    if not resume.profile:
        raise HTTPException(status_code=400, detail="Resume not yet parsed")

    # Verify job role or job description
    job_role = None
    job_description = None

    if interview_data.job_role_id:
        job_role = db.query(JobRole).filter(JobRole.id == interview_data.job_role_id).first()
        if not job_role:
            raise HTTPException(status_code=404, detail="Job role not found")

    if interview_data.job_description_id:
        job_description = db.query(JobDescription).filter(
            JobDescription.id == interview_data.job_description_id
        ).first()
        if not job_description:
            raise HTTPException(status_code=404, detail="Job description not found")
        check_resource_access(current_user, job_description.user_id)

    if not job_role and not job_description:
        raise HTTPException(status_code=400, detail="Either job_role_id or job_description_id is required")

    # Create interview
    interview = Interview(
        user_id=current_user.id,
        resume_id=resume.id,
        job_role_id=interview_data.job_role_id,
        job_description_id=interview_data.job_description_id,
        difficulty=interview_data.difficulty,
        status=InterviewStatus.CREATED
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    return InterviewResponse.model_validate(interview)


@router.post("/{interview_id}/start", response_model=QuestionResponse)
async def start_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start interview and get first question"""

    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    check_resource_access(current_user, interview.user_id)

    if interview.status != InterviewStatus.CREATED:
        raise HTTPException(status_code=400, detail="Interview already started or completed")

    # Build interview context
    profile = interview.resume.profile
    job_profile = _build_job_profile(interview)

    # Create blueprint
    planner = InterviewPlanner()
    try:
        blueprint = await planner.create_interview_blueprint(
            profile_data=_profile_to_dict(profile),
            job_profile=job_profile,
            difficulty=interview.difficulty.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create interview plan: {str(e)}")

    # Generate first question
    generator = QuestionGenerator()
    interview_context = {
        'profile_summary': _profile_to_dict(profile),
        'job_title': job_profile.get('title'),
        'blueprint': blueprint,
        'difficulty': interview.difficulty.value
    }

    try:
        question_data = await generator.generate_next_question(
            interview_context=interview_context,
            previous_questions=[],
            previous_evaluations=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

    # Save question
    question = InterviewQuestion(
        interview_id=interview.id,
        question_number=1,
        question_type=QuestionType(question_data.get('type', 'technical')),
        question_text=question_data.get('question'),
        difficulty=question_data.get('difficulty'),
        skill_being_tested=question_data.get('skill'),
        context=question_data,
        is_followup=False
    )

    db.add(question)

    # Update interview status
    interview.status = InterviewStatus.IN_PROGRESS
    interview.started_at = datetime.utcnow()
    interview.interview_blueprint = blueprint
    interview.state_data = {
        'current_question': 1,
        'total_questions': blueprint.get('total_questions', 15),
        'context': interview_context
    }

    db.commit()
    db.refresh(question)

    return QuestionResponse.model_validate(question)


@router.post("/{interview_id}/answer", response_model=QuestionResponse)
async def submit_answer(
    interview_id: int,
    answer_data: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answer and get next question"""

    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    check_resource_access(current_user, interview.user_id)

    if interview.status != InterviewStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Interview is not in progress")

    # Get current question
    state_data = interview.state_data or {}
    current_q_num = state_data.get('current_question', 1)

    current_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview.id,
        InterviewQuestion.question_number == current_q_num
    ).first()

    if not current_question:
        raise HTTPException(status_code=404, detail="Current question not found")

    # Check if already answered
    if current_question.answer:
        raise HTTPException(status_code=400, detail="Question already answered")

    # Save answer
    answer = InterviewAnswer(
        question_id=current_question.id,
        answer_text=answer_data.answer_text
    )
    db.add(answer)
    db.flush()

    # Evaluate answer
    evaluator = AnswerEvaluator()
    profile = interview.resume.profile

    # Get claimed level for the skill
    skill_name = current_question.skill_being_tested
    claimed_level = None
    if skill_name and profile:
        skill = next((s for s in profile.skills if s.skill_name.lower() == skill_name.lower()), None)
        if skill:
            claimed_level = skill.claimed_level.value if skill.claimed_level else None

    try:
        eval_data = await evaluator.evaluate_answer(
            question={'question': current_question.question_text, 'type': current_question.question_type.value,
                     'skill': current_question.skill_being_tested, 'difficulty': current_question.difficulty},
            answer=answer_data.answer_text,
            context={'claimed_level': claimed_level}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answer: {str(e)}")

    # Save evaluation
    evaluation = AnswerEvaluation(
        answer_id=answer.id,
        overall_score=eval_data.get('overall_score', 0),
        correctness_score=eval_data.get('correctness_score'),
        technical_depth_score=eval_data.get('technical_depth_score'),
        relevance_score=eval_data.get('relevance_score'),
        clarity_score=eval_data.get('clarity_score'),
        problem_solving_score=eval_data.get('problem_solving_score'),
        strengths=eval_data.get('strengths', []),
        weaknesses=eval_data.get('weaknesses', []),
        evidence=eval_data.get('evidence', []),
        skill_level_demonstrated=eval_data.get('skill_level_demonstrated'),
        feedback=eval_data.get('feedback')
    )
    db.add(evaluation)
    db.commit()

    # Check if should generate follow-up
    should_followup = eval_data.get('should_followup', False) and current_q_num < 20

    # Decide next question
    total_questions = state_data.get('total_questions', 15)

    if current_q_num >= total_questions:
        # Interview complete
        interview.status = InterviewStatus.COMPLETED
        interview.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=200, detail="Interview completed")

    # Generate next question
    generator = QuestionGenerator()
    previous_questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview.id
    ).order_by(InterviewQuestion.question_number).all()

    previous_evaluations = []
    for q in previous_questions:
        if q.answer and q.answer.evaluation:
            previous_evaluations.append({
                'overall_score': q.answer.evaluation.overall_score,
                'skill_level_demonstrated': q.answer.evaluation.skill_level_demonstrated.value if q.answer.evaluation.skill_level_demonstrated else None
            })

    interview_context = state_data.get('context', {})

    try:
        question_data = await generator.generate_next_question(
            interview_context=interview_context,
            previous_questions=[{'type': q.question_type.value, 'skill': q.skill_being_tested, 'question': q.question_text} for q in previous_questions],
            previous_evaluations=previous_evaluations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate next question: {str(e)}")

    # Create next question
    next_question = InterviewQuestion(
        interview_id=interview.id,
        question_number=current_q_num + 1,
        question_type=QuestionType(question_data.get('type', 'technical')),
        question_text=question_data.get('question'),
        difficulty=question_data.get('difficulty'),
        skill_being_tested=question_data.get('skill'),
        context=question_data,
        is_followup=question_data.get('is_followup', False),
        parent_question_id=current_question.id if question_data.get('is_followup') else None
    )

    db.add(next_question)

    # Update interview state
    state_data['current_question'] = current_q_num + 1
    interview.state_data = state_data

    db.commit()
    db.refresh(next_question)

    return QuestionResponse.model_validate(next_question)


@router.post("/{interview_id}/finish", status_code=status.HTTP_200_OK)
async def finish_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually finish interview"""

    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    check_resource_access(current_user, interview.user_id)

    if interview.status == InterviewStatus.COMPLETED:
        return {"message": "Interview already completed"}

    interview.status = InterviewStatus.COMPLETED
    interview.completed_at = datetime.utcnow()
    db.commit()

    return {"message": "Interview completed successfully"}


@router.get("", response_model=List[InterviewResponse])
async def list_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's interviews"""
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.created_at.desc()).all()
    return [InterviewResponse.model_validate(i) for i in interviews]


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interview details"""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    check_resource_access(current_user, interview.user_id)
    return InterviewResponse.model_validate(interview)


def _build_job_profile(interview: Interview) -> Dict[str, Any]:
    """Build job profile from interview"""
    if interview.job_role:
        return {
            'title': interview.job_role.title,
            'required_skills': interview.job_role.required_skills or [],
            'preferred_skills': interview.job_role.preferred_skills or [],
            'responsibilities': interview.job_role.responsibilities or []
        }
    elif interview.job_description:
        return {
            'title': interview.job_description.title,
            'required_skills': interview.job_description.required_skills or [],
            'preferred_skills': interview.job_description.preferred_skills or [],
            'responsibilities': []
        }
    return {'title': 'Unknown', 'required_skills': [], 'preferred_skills': [], 'responsibilities': []}


def _profile_to_dict(profile) -> Dict[str, Any]:
    """Convert profile to dictionary"""
    return {
        'full_name': profile.full_name,
        'total_experience_years': profile.total_experience_years,
        'skills': [{'name': s.skill_name, 'level': s.claimed_level.value if s.claimed_level else None, 'category': s.category.value} for s in profile.skills],
        'projects': [{'name': p.project_name, 'technologies': p.technologies} for p in profile.projects],
        'experiences': [{'company': e.company_name, 'title': e.job_title} for e in profile.experiences]
    }
