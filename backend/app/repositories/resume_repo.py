from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.resume import (
    Resume,
    CandidateProfile,
    CandidateSkill,
    Project,
    Experience,
    Certification,
)

class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, resume_id: int, user_id: Optional[int] = None) -> Optional[Resume]:
        query = self.db.query(Resume).filter(Resume.id == resume_id, Resume.is_deleted == False)
        if user_id:
            query = query.filter(Resume.user_id == user_id)
        return query.first()

    def list_by_user(self, user_id: int) -> List[Resume]:
        return self.db.query(Resume).filter(
            Resume.user_id == user_id,
            Resume.is_deleted == False
        ).order_by(Resume.created_at.desc()).all()

    def create_resume(self, user_id: int, file_name: str, file_path: str, file_size: int, file_hash: Optional[str] = None, raw_text: Optional[str] = None) -> Resume:
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            raw_text=raw_text,
            status="pending"
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def update_resume_status(self, resume: Resume, status: str, raw_text: Optional[str] = None) -> Resume:
        resume.status = status
        if raw_text:
            resume.raw_text = raw_text
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def create_or_update_profile(self, resume: Resume, profile_data: Dict[str, Any]) -> CandidateProfile:
        profile = self.db.query(CandidateProfile).filter(CandidateProfile.resume_id == resume.id).first()
        if not profile:
            profile = CandidateProfile(
                resume_id=resume.id,
                user_id=resume.user_id,
                full_name=profile_data.get("full_name"),
                email=profile_data.get("email"),
                phone=profile_data.get("phone"),
                headline=profile_data.get("headline"),
                summary=profile_data.get("summary"),
                total_experience_years=profile_data.get("total_experience_years", 0.0),
                education_json=profile_data.get("education_json", []),
                raw_parsed_data=profile_data
            )
            self.db.add(profile)
            self.db.flush()
        else:
            profile.full_name = profile_data.get("full_name", profile.full_name)
            profile.email = profile_data.get("email", profile.email)
            profile.phone = profile_data.get("phone", profile.phone)
            profile.headline = profile_data.get("headline", profile.headline)
            profile.summary = profile_data.get("summary", profile.summary)
            profile.total_experience_years = profile_data.get("total_experience_years", profile.total_experience_years)
            profile.education_json = profile_data.get("education_json", profile.education_json)
            profile.raw_parsed_data = profile_data

        # Clear existing child entities and recreate
        self.db.query(CandidateSkill).filter(CandidateSkill.candidate_profile_id == profile.id).delete()
        self.db.query(Project).filter(Project.candidate_profile_id == profile.id).delete()
        self.db.query(Experience).filter(Experience.candidate_profile_id == profile.id).delete()
        self.db.query(Certification).filter(Certification.candidate_profile_id == profile.id).delete()

        # Add skills
        for sk in profile_data.get("skills", []):
            if isinstance(sk, dict) and sk.get("skill_name"):
                skill_obj = CandidateSkill(
                    candidate_profile_id=profile.id,
                    skill_name=sk.get("skill_name"),
                    category=sk.get("category", "technical"),
                    claimed_level=sk.get("claimed_level", "intermediate"),
                    years_of_exp=float(sk.get("years_of_exp", 1.0)),
                    context_evidence=sk.get("context_evidence")
                )
                self.db.add(skill_obj)

        # Add projects
        for pr in profile_data.get("projects", []):
            if isinstance(pr, dict) and pr.get("title"):
                proj_obj = Project(
                    candidate_profile_id=profile.id,
                    title=pr.get("title"),
                    role=pr.get("role"),
                    description=pr.get("description"),
                    tech_stack_json=pr.get("tech_stack_json", []),
                    achievements_json=pr.get("achievements_json", []),
                    url=pr.get("url")
                )
                self.db.add(proj_obj)

        # Add experience
        for exp in profile_data.get("experiences", []):
            if isinstance(exp, dict) and exp.get("company"):
                exp_obj = Experience(
                    candidate_profile_id=profile.id,
                    company=exp.get("company"),
                    title=exp.get("title", ""),
                    location=exp.get("location"),
                    start_date=exp.get("start_date"),
                    end_date=exp.get("end_date"),
                    is_current=exp.get("is_current", False),
                    responsibilities_json=exp.get("responsibilities_json", [])
                )
                self.db.add(exp_obj)

        # Add certifications
        for cert in profile_data.get("certifications", []):
            if isinstance(cert, dict) and cert.get("name"):
                cert_obj = Certification(
                    candidate_profile_id=profile.id,
                    name=cert.get("name"),
                    issuer=cert.get("issuer"),
                    issue_date=cert.get("issue_date"),
                    credential_id=cert.get("credential_id"),
                    credential_url=cert.get("credential_url")
                )
                self.db.add(cert_obj)

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def soft_delete_resume(self, resume: Resume) -> bool:
        resume.is_deleted = True
        self.db.commit()
        return True
