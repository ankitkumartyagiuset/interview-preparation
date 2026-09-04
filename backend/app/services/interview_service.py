from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.interview_repo import InterviewRepository
from app.repositories.resume_repo import ResumeRepository
from app.repositories.job_repo import JobRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.audit_repo import AuditRepository
from app.ai.engines.interview_planner import interview_planner_engine
from app.ai.engines.question_gen import question_generator_engine, follow_up_generator_engine
from app.ai.engines.answer_evaluator import answer_evaluator_engine
from app.ai.engines.skill_gap_engine import skill_gap_engine
from app.ai.engines.roadmap_engine import roadmap_engine
from app.ai.engines.report_engine import report_engine
from app.models.interview import Interview, InterviewQuestion, InterviewAnswer

class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        self.interview_repo = InterviewRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.job_repo = JobRepository(db)
        self.report_repo = ReportRepository(db)
        self.audit_repo = AuditRepository(db)

    async def create_interview(
        self,
        user_id: int,
        title: Optional[str] = None,
        resume_id: Optional[int] = None,
        job_role_id: Optional[int] = None,
        job_description_id: Optional[int] = None,
        interview_type: str = "mixed",
        difficulty: str = "intermediate",
        total_questions: int = 5,
        custom_blueprint: Optional[Dict[str, Any]] = None,
        provider_name: Optional[str] = None
    ) -> Interview:
        # Determine title
        if not title:
            if job_role_id:
                role = self.job_repo.get_role_by_id(job_role_id)
                title = f"{role.title if role else 'Custom'} Competency Interview"
            elif job_description_id:
                jd = self.job_repo.get_jd_by_id(job_description_id, user_id)
                title = f"{jd.title if jd else 'Job Description'} Interview"
            else:
                title = "Software Engineering Competency Interview"

        blueprint = custom_blueprint or interview_planner_engine.generate_default_blueprint(
            interview_type=interview_type,
            total_questions=total_questions
        )

        interview = self.interview_repo.create_interview(
            user_id=user_id,
            title=title,
            resume_id=resume_id,
            job_role_id=job_role_id,
            job_description_id=job_description_id,
            interview_type=interview_type,
            difficulty=difficulty,
            total_questions=total_questions,
            blueprint_json=blueprint
        )

        self.audit_repo.log(
            user_id=user_id,
            action="INTERVIEW_CREATED",
            resource_type="interview",
            resource_id=str(interview.id),
            details_json={"type": interview_type, "difficulty": difficulty}
        )

        return interview

    async def start_interview(self, interview_id: int, user_id: int, provider_name: Optional[str] = None) -> Dict[str, Any]:
        interview = self.interview_repo.get_by_id(interview_id, user_id=user_id)
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")

        if interview.status == "completed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This interview is already completed.")

        # Update status
        self.interview_repo.start_interview(interview)

        # Check if question 1 already generated
        if interview.questions:
            first_q = interview.questions[0]
        else:
            # Generate first question
            candidate_summary = self._build_candidate_summary(interview)
            target_role = self._get_target_role_name(interview)

            q_data = await question_generator_engine.generate_next_question(
                candidate_summary=candidate_summary,
                target_role=target_role,
                blueprint=interview.blueprint_json or {},
                sequence_num=1,
                difficulty=interview.difficulty,
                previous_questions=[],
                previous_scores=[],
                current_skill_confidence={},
                provider_name=provider_name
            )

            first_q = self.interview_repo.add_question(
                interview_id=interview.id,
                sequence_num=1,
                category=q_data.get("category", "technical"),
                target_skill=q_data.get("target_skill", "Python"),
                difficulty=q_data.get("difficulty", interview.difficulty),
                question_text=q_data.get("question_text", "Could you walk us through your background and key technical achievements?"),
                context_rationale=q_data.get("context_rationale"),
                is_follow_up=False
            )

            # Update interview state
            state = interview.state_json or {}
            state["previous_questions"] = [first_q.question_text]
            self.interview_repo.update_interview_state(interview, state, current_index=1)

        return {
            "interview_id": interview.id,
            "title": interview.title,
            "total_questions": interview.total_questions,
            "first_question": first_q,
            "status": interview.status
        }

    async def submit_answer(
        self,
        interview_id: int,
        user_id: int,
        question_id: int,
        answer_text: str,
        time_taken_seconds: int = 0,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        interview = self.interview_repo.get_by_id(interview_id, user_id=user_id)
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found.")

        if interview.status == "completed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Interview has already finished.")

        question = self.interview_repo.get_question_by_id(question_id)
        if not question or question.interview_id != interview.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question for this interview.")

        # Save candidate answer
        answer = self.interview_repo.add_answer(
            question_id=question.id,
            answer_text=answer_text,
            time_taken_seconds=time_taken_seconds
        )

        # 1. Evaluate Answer using AnswerEvaluatorEngine
        target_role = self._get_target_role_name(interview)
        claimed_lvl = self._get_claimed_level_for_skill(interview, question.target_skill)

        eval_res = await answer_evaluator_engine.evaluate_answer(
            question_text=question.question_text,
            target_skill=question.target_skill or "General",
            claimed_level=claimed_lvl,
            candidate_answer=answer_text,
            target_role=target_role,
            provider_name=provider_name
        )

        # Save evaluation record
        evaluation = self.interview_repo.add_evaluation(
            answer_id=answer.id,
            score=eval_res.get("score", 7.0),
            correctness=eval_res.get("correctness", 7.0),
            technical_depth=eval_res.get("technical_depth", 7.0),
            relevance=eval_res.get("relevance", 7.0),
            clarity=eval_res.get("clarity", 7.0),
            communication=eval_res.get("communication", 7.0),
            problem_solving=eval_res.get("problem_solving", 7.0),
            strengths_json=eval_res.get("strengths", []),
            weaknesses_json=eval_res.get("weaknesses", []),
            evidence_json=eval_res.get("evidence", []),
            demonstrated_skill_level=eval_res.get("demonstrated_skill_level", "intermediate"),
            feedback_summary=eval_res.get("feedback_summary")
        )

        # 2. Update Interview State
        state = interview.state_json or {}
        prev_questions = state.get("previous_questions", [])
        prev_scores = state.get("previous_scores", [])
        skill_conf = state.get("skill_confidence", {})

        prev_scores.append(evaluation.score)
        if question.target_skill:
            skill_conf[question.target_skill] = evaluation.score

        state["previous_questions"] = prev_questions
        state["previous_scores"] = prev_scores
        state["skill_confidence"] = skill_conf

        current_idx = interview.current_question_index or 1
        answered_count = len(prev_scores)

        # 3. Check if we should conclude the interview
        if answered_count >= interview.total_questions:
            await self._finalize_interview(interview, user_id, provider_name)
            return {
                "evaluation_id": evaluation.id,
                "feedback_summary": evaluation.feedback_summary,
                "next_question": None,
                "is_finished": True,
                "current_question_index": answered_count,
                "total_questions": interview.total_questions
            }

        # 4. Check for dynamic follow-up condition
        # Only allow follow-up if not already a follow-up and answered count < total_questions
        next_seq = answered_count + 1
        follow_up_generated = False
        next_q_obj = None

        if not question.is_follow_up and evaluation.score < 7.0 and answered_count < (interview.total_questions - 1):
            fu_res = await follow_up_generator_engine.evaluate_and_generate_follow_up(
                question_text=question.question_text,
                candidate_answer=answer_text,
                target_skill=question.target_skill or "General",
                provider_name=provider_name
            )
            if fu_res.get("should_follow_up") and fu_res.get("question_text"):
                next_q_obj = self.interview_repo.add_question(
                    interview_id=interview.id,
                    sequence_num=next_seq,
                    category=fu_res.get("category", question.category),
                    target_skill=fu_res.get("target_skill", question.target_skill),
                    difficulty=fu_res.get("difficulty", question.difficulty),
                    question_text=fu_res.get("question_text"),
                    context_rationale=fu_res.get("context_rationale"),
                    is_follow_up=True,
                    parent_question_id=question.id
                )
                follow_up_generated = True

        if not follow_up_generated:
            # 5. Adapt difficulty and generate next distinct question
            recent_score = evaluation.score
            if recent_score >= 8.5:
                curr_difficulty = "advanced"
            elif recent_score >= 6.5:
                curr_difficulty = "intermediate"
            else:
                curr_difficulty = "beginner"

            candidate_summary = self._build_candidate_summary(interview)
            q_data = await question_generator_engine.generate_next_question(
                candidate_summary=candidate_summary,
                target_role=target_role,
                blueprint=interview.blueprint_json or {},
                sequence_num=next_seq,
                difficulty=curr_difficulty,
                previous_questions=prev_questions,
                previous_scores=prev_scores,
                current_skill_confidence=skill_conf,
                provider_name=provider_name
            )

            next_q_obj = self.interview_repo.add_question(
                interview_id=interview.id,
                sequence_num=next_seq,
                category=q_data.get("category", "technical"),
                target_skill=q_data.get("target_skill", "General"),
                difficulty=q_data.get("difficulty", curr_difficulty),
                question_text=q_data.get("question_text"),
                context_rationale=q_data.get("context_rationale"),
                is_follow_up=False
            )

        prev_questions.append(next_q_obj.question_text)
        state["previous_questions"] = prev_questions
        self.interview_repo.update_interview_state(interview, state, current_index=next_seq)

        return {
            "evaluation_id": evaluation.id,
            "feedback_summary": evaluation.feedback_summary,
            "next_question": next_q_obj,
            "is_finished": False,
            "current_question_index": next_seq,
            "total_questions": interview.total_questions
        }

    async def _finalize_interview(self, interview: Interview, user_id: int, provider_name: Optional[str] = None):
        """Calculates skill gaps, 7-day roadmap, and final readiness report."""
        # Gather all questions, answers & evaluations
        evaluations_list = []
        evals_by_skill = {}

        for q in interview.questions:
            if q.answer and q.answer.evaluation:
                ev = q.answer.evaluation
                ev_dict = {
                    "category": q.category,
                    "target_skill": q.target_skill,
                    "score": ev.score,
                    "strengths_json": ev.strengths_json or [],
                    "weaknesses_json": ev.weaknesses_json or [],
                    "demonstrated_skill_level": ev.demonstrated_skill_level,
                    "feedback_summary": ev.feedback_summary
                }
                evaluations_list.append(ev_dict)
                if q.target_skill:
                    s_key = q.target_skill.lower()
                    if s_key not in evs_by_skill:
                        evs_by_skill[s_key] = []
                    evs_by_skill[s_key].append(ev_dict)

        # Required & Claimed Skills
        required_skills = self._get_required_skills(interview)
        claimed_skills = self._get_claimed_skills(interview)

        # 1. Calculate Skill Gaps
        skill_gaps = skill_gap_engine.calculate_gaps(
            required_skills=required_skills,
            claimed_skills=claimed_skills,
            evaluations_by_skill=evs_by_skill
        )
        self.report_repo.save_skill_gaps(interview.id, user_id, skill_gaps)

        # 2. Candidate & Role metadata
        candidate_name = self._get_candidate_name(interview)
        target_role = self._get_target_role_name(interview)

        # 3. Generate Final Report
        report_data = await report_engine.generate_final_report(
            candidate_name=candidate_name,
            target_role=target_role,
            evaluations=evaluations_list,
            skill_gaps=skill_gaps,
            blueprint=interview.blueprint_json or {},
            provider_name=provider_name
        )
        saved_report = self.report_repo.save_report(interview.id, user_id, report_data)

        # 4. Generate 7-Day Roadmap
        roadmap_data = await roadmap_engine.generate_roadmap(
            target_role=target_role,
            skill_gaps=skill_gaps,
            overall_readiness=saved_report.overall_readiness_score,
            provider_name=provider_name
        )
        self.report_repo.save_roadmap(
            interview_id=interview.id,
            user_id=user_id,
            title=roadmap_data.get("title", f"7-Day Skill Improvement Plan: {target_role}"),
            duration_days=roadmap_data.get("duration_days", 7),
            summary=roadmap_data.get("summary", ""),
            overall_recommendation=roadmap_data.get("overall_recommendation", ""),
            items=roadmap_data.get("items", [])
        )

        # 5. Finish Interview
        self.interview_repo.finish_interview(interview, overall_score=saved_report.overall_readiness_score)

        self.audit_repo.log(
            user_id=user_id,
            action="INTERVIEW_COMPLETED",
            resource_type="interview",
            resource_id=str(interview.id),
            details_json={"overall_score": saved_report.overall_readiness_score}
        )

    def get_interview(self, interview_id: int, user_id: int) -> Interview:
        interview = self.interview_repo.get_by_id(interview_id, user_id=user_id)
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found.")
        return interview

    def list_interviews(self, user_id: int) -> List[Interview]:
        return self.interview_repo.list_by_user(user_id)

    # --- Private Helpers ---
    def _build_candidate_summary(self, interview: Interview) -> str:
        if interview.resume and interview.resume.candidate_profile:
            p = interview.resume.candidate_profile
            skills_str = ", ".join([f"{s.skill_name} ({s.claimed_level})" for s in p.skills[:10]])
            projects_str = ", ".join([f"{pr.title}: {pr.description or ''}" for pr in p.projects[:3]])
            return f"Headline: {p.headline}\nSkills: {skills_str}\nKey Projects: {projects_str}"
        return "Software Engineer with general backend and web development background."

    def _get_target_role_name(self, interview: Interview) -> str:
        if interview.job_role:
            return interview.job_role.title
        elif interview.job_description:
            return interview.job_description.title
        return "Software Engineer"

    def _get_claimed_level_for_skill(self, interview: Interview, skill_name: Optional[str]) -> str:
        if not skill_name or not interview.resume or not interview.resume.candidate_profile:
            return "intermediate"
        for s in interview.resume.candidate_profile.skills:
            if s.skill_name.lower() == skill_name.lower():
                return s.claimed_level
        return "intermediate"

    def _get_required_skills(self, interview: Interview) -> List[Dict[str, Any]]:
        if interview.job_role and interview.job_role.core_skills_json:
            return interview.job_role.core_skills_json
        elif interview.job_description and interview.job_description.required_skills_json:
            return interview.job_description.required_skills_json
        return [
            {"name": "Python", "level": "advanced", "category": "programming"},
            {"name": "FastAPI", "level": "intermediate", "category": "framework"},
            {"name": "PostgreSQL", "level": "advanced", "category": "database"},
            {"name": "System Design", "level": "intermediate", "category": "architecture"}
        ]

    def _get_claimed_skills(self, interview: Interview) -> List[Dict[str, Any]]:
        if interview.resume and interview.resume.candidate_profile:
            return [
                {
                    "skill_name": s.skill_name,
                    "category": s.category,
                    "claimed_level": s.claimed_level,
                    "years_of_exp": s.years_of_exp
                }
                for s in interview.resume.candidate_profile.skills
            ]
        return []

    def _get_candidate_name(self, interview: Interview) -> str:
        if interview.resume and interview.resume.candidate_profile and interview.resume.candidate_profile.full_name:
            return interview.resume.candidate_profile.full_name
        elif interview.user:
            return interview.user.full_name
        return "Candidate"
