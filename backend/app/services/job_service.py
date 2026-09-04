from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.repositories.job_repo import JobRepository
from backend.app.repositories.resume_repo import ResumeRepository
from backend.app.ai.engines.jd_analyzer import jd_analyzer_engine
from backend.app.models.job import JobRole, JobDescription

class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)
        self.resume_repo = ResumeRepository(db)

    def list_roles(self) -> List[JobRole]:
        return self.job_repo.list_roles()

    def get_role(self, role_id: int) -> JobRole:
        role = self.job_repo.get_role_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job role not found."
            )
        return role

    async def create_job_description(
        self,
        user_id: int,
        title: str,
        company: Optional[str],
        raw_text: str,
        seniority: str = "intermediate",
        provider_name: Optional[str] = None
    ) -> JobDescription:
        # Analyze JD using AI Engine
        analyzed = await jd_analyzer_engine.analyze_job_description(raw_text, role_title_hint=title, provider_name=provider_name)
        
        req_skills = analyzed.get("required_skills_json", [])
        pref_skills = analyzed.get("preferred_skills_json", [])
        responsibilities = analyzed.get("responsibilities_json", [])
        exp_years = float(analyzed.get("experience_years_required", 2.0))
        seniority_level = analyzed.get("seniority", seniority)

        return self.job_repo.create_jd(
            user_id=user_id,
            title=title,
            company=company,
            raw_text=raw_text,
            required_skills_json=req_skills,
            preferred_skills_json=pref_skills,
            responsibilities_json=responsibilities,
            seniority=seniority_level,
            experience_years_required=exp_years
        )

    def match_resume_with_role(
        self,
        resume_id: int,
        user_id: int,
        job_role_id: Optional[int] = None,
        job_description_id: Optional[int] = None
    ) -> Dict[str, Any]:
        resume = self.resume_repo.get_by_id(resume_id, user_id)
        if not resume or not resume.candidate_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid resume with parsed profile is required for matching."
            )

        candidate_skills = {s.skill_name.lower(): s for s in resume.candidate_profile.skills}

        target_required_skills = []
        target_preferred_skills = []

        if job_role_id:
            role = self.job_repo.get_role_by_id(job_role_id)
            if role:
                target_required_skills = role.core_skills_json or []
        elif job_description_id:
            jd = self.job_repo.get_jd_by_id(job_description_id, user_id)
            if jd:
                target_required_skills = jd.required_skills_json or []
                target_preferred_skills = jd.preferred_skills_json or []

        matched_skills = []
        missing_skills = []
        weak_skills = []

        for req in target_required_skills:
            req_name = req.get("name", "")
            req_name_lower = req_name.lower()
            req_level = req.get("level", "intermediate").lower()

            if req_name_lower in candidate_skills:
                c_skill = candidate_skills[req_name_lower]
                matched_skills.append({
                    "name": req_name,
                    "claimed_level": c_skill.claimed_level,
                    "required_level": req_level,
                    "category": req.get("category", "technical")
                })
            else:
                missing_skills.append({
                    "name": req_name,
                    "required_level": req_level,
                    "category": req.get("category", "technical")
                })

        total_req = len(target_required_skills) or 1
        match_score = round((len(matched_skills) / total_req) * 100.0, 1)

        # Relevant projects
        relevant_projects = []
        for p in resume.candidate_profile.projects:
            relevant_projects.append(p.title)

        # Recommended interview topics
        recommended_topics = [s["name"] for s in matched_skills[:3]] + [s["name"] for s in missing_skills[:2]]
        if not recommended_topics:
            recommended_topics = ["Core Programming & Architecture", "System Design", "Problem Solving"]

        readiness_label = "Interview Ready" if match_score >= 75 else "Developing" if match_score >= 50 else "Preparation Needed"

        return {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "weak_skills": weak_skills,
            "relevant_projects": relevant_projects[:3],
            "recommended_topics": recommended_topics,
            "readiness_label": readiness_label
        }
