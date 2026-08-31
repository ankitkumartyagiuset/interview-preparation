from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.job import JobRole, JobDescription

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_role_by_id(self, role_id: int) -> Optional[JobRole]:
        return self.db.query(JobRole).filter(JobRole.id == role_id).first()

    def get_role_by_title(self, title: str) -> Optional[JobRole]:
        return self.db.query(JobRole).filter(JobRole.title.ilike(title.strip())).first()

    def list_roles(self) -> List[JobRole]:
        return self.db.query(JobRole).order_by(JobRole.title.asc()).all()

    def create_role(
        self,
        title: str,
        department: Optional[str] = None,
        seniority: str = "intermediate",
        description: Optional[str] = None,
        core_skills_json: Optional[List[Dict[str, Any]]] = None,
        default_blueprint_json: Optional[Dict[str, Any]] = None
    ) -> JobRole:
        role = JobRole(
            title=title.strip(),
            department=department,
            seniority=seniority,
            description=description,
            core_skills_json=core_skills_json or [],
            default_blueprint_json=default_blueprint_json or {}
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_jd_by_id(self, jd_id: int, user_id: Optional[int] = None) -> Optional[JobDescription]:
        query = self.db.query(JobDescription).filter(JobDescription.id == jd_id)
        if user_id:
            query = query.filter(JobDescription.user_id == user_id)
        return query.first()

    def list_jds_by_user(self, user_id: int) -> List[JobDescription]:
        return self.db.query(JobDescription).filter(JobDescription.user_id == user_id).order_by(JobDescription.created_at.desc()).all()

    def create_jd(
        self,
        user_id: int,
        title: str,
        company: Optional[str],
        raw_text: str,
        required_skills_json: List[Dict[str, Any]],
        preferred_skills_json: List[Dict[str, Any]],
        responsibilities_json: List[str],
        seniority: str = "intermediate",
        experience_years_required: float = 2.0
    ) -> JobDescription:
        jd = JobDescription(
            user_id=user_id,
            title=title,
            company=company,
            raw_text=raw_text,
            required_skills_json=required_skills_json,
            preferred_skills_json=preferred_skills_json,
            responsibilities_json=responsibilities_json,
            seniority=seniority,
            experience_years_required=experience_years_required
        )
        self.db.add(jd)
        self.db.commit()
        self.db.refresh(jd)
        return jd
