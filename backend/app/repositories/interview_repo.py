from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.interview import (
    Interview,
    InterviewQuestion,
    InterviewAnswer,
    AnswerEvaluation,
)

class InterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, interview_id: int, user_id: Optional[int] = None) -> Optional[Interview]:
        query = self.db.query(Interview).filter(Interview.id == interview_id)
        if user_id:
            query = query.filter(Interview.user_id == user_id)
        return query.first()

    def list_by_user(self, user_id: int, limit: int = 50) -> List[Interview]:
        return self.db.query(Interview).filter(
            Interview.user_id == user_id
        ).order_by(Interview.created_at.desc()).limit(limit).all()

    def create_interview(
        self,
        user_id: int,
        title: str,
        resume_id: Optional[int] = None,
        job_role_id: Optional[int] = None,
        job_description_id: Optional[int] = None,
        interview_type: str = "mixed",
        difficulty: str = "intermediate",
        total_questions: int = 5,
        blueprint_json: Optional[Dict[str, Any]] = None
    ) -> Interview:
        interview = Interview(
            user_id=user_id,
            resume_id=resume_id,
            job_role_id=job_role_id,
            job_description_id=job_description_id,
            title=title,
            interview_type=interview_type,
            difficulty=difficulty,
            total_questions=total_questions,
            blueprint_json=blueprint_json or {},
            status="created",
            state_json={
                "previous_questions": [],
                "previous_scores": [],
                "skill_confidence": {},
                "topics_covered": []
            }
        )
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def start_interview(self, interview: Interview) -> Interview:
        interview.status = "in_progress"
        interview.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def finish_interview(self, interview: Interview, overall_score: float) -> Interview:
        interview.status = "completed"
        interview.overall_score = overall_score
        interview.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def add_question(
        self,
        interview_id: int,
        sequence_num: int,
        category: str,
        target_skill: str,
        difficulty: str,
        question_text: str,
        context_rationale: Optional[str] = None,
        is_follow_up: bool = False,
        parent_question_id: Optional[int] = None
    ) -> InterviewQuestion:
        q = InterviewQuestion(
            interview_id=interview_id,
            sequence_num=sequence_num,
            category=category,
            target_skill=target_skill,
            difficulty=difficulty,
            question_text=question_text,
            context_rationale=context_rationale,
            is_follow_up=is_follow_up,
            parent_question_id=parent_question_id
        )
        self.db.add(q)
        self.db.commit()
        self.db.refresh(q)
        return q

    def get_question_by_id(self, question_id: int) -> Optional[InterviewQuestion]:
        return self.db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()

    def add_answer(
        self,
        question_id: int,
        answer_text: str,
        time_taken_seconds: int = 0,
        audio_url: Optional[str] = None
    ) -> InterviewAnswer:
        ans = InterviewAnswer(
            question_id=question_id,
            answer_text=answer_text,
            time_taken_seconds=time_taken_seconds,
            audio_url=audio_url
        )
        self.db.add(ans)
        self.db.commit()
        self.db.refresh(ans)
        return ans

    def add_evaluation(
        self,
        answer_id: int,
        score: float,
        correctness: float,
        technical_depth: float,
        relevance: float,
        clarity: float,
        communication: float,
        problem_solving: float,
        strengths_json: List[str],
        weaknesses_json: List[str],
        evidence_json: List[str],
        demonstrated_skill_level: str,
        feedback_summary: Optional[str] = None
    ) -> AnswerEvaluation:
        ev = AnswerEvaluation(
            answer_id=answer_id,
            score=score,
            correctness=correctness,
            technical_depth=technical_depth,
            relevance=relevance,
            clarity=clarity,
            communication=communication,
            problem_solving=problem_solving,
            strengths_json=strengths_json,
            weaknesses_json=weaknesses_json,
            evidence_json=evidence_json,
            demonstrated_skill_level=demonstrated_skill_level,
            feedback_summary=feedback_summary
        )
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev

    def update_interview_state(self, interview: Interview, state_json: Dict[str, Any], current_index: int) -> Interview:
        interview.state_json = state_json
        interview.current_question_index = current_index
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def count_interviews(self) -> int:
        return self.db.query(Interview).count()
