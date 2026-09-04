from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.resume import Resume
from app.models.interview import Interview
from app.models.skill_gap import SkillGap
from app.models.audit_log import AuditLog
from app.repositories.user_repo import UserRepository
from app.repositories.audit_repo import AuditRepository

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def get_analytics(self) -> Dict[str, Any]:
        total_users = self.db.query(func.count(User.id)).scalar() or 0
        total_resumes = self.db.query(func.count(Resume.id)).filter(Resume.is_deleted == False).scalar() or 0
        total_interviews = self.db.query(func.count(Interview.id)).scalar() or 0
        completed_interviews = self.db.query(func.count(Interview.id)).filter(Interview.status == "completed").scalar() or 0
        
        avg_score = self.db.query(func.avg(Interview.overall_score)).filter(Interview.status == "completed").scalar() or 0.0

        # Role distribution
        role_counts = self.db.query(User.role, func.count(User.id)).group_by(User.role).all()
        role_dist = {r: count for r, count in role_counts}

        # Top Skill Gaps across platform
        gaps = self.db.query(
            SkillGap.skill_name,
            func.count(SkillGap.id).label("gap_count")
        ).group_by(SkillGap.skill_name).order_by(func.count(SkillGap.id).desc()).limit(5).all()

        top_gaps = [{"skill": g[0], "count": g[1]} for g in gaps]

        # Recent activity audit
        recent_logs = self.audit_repo.list_logs(limit=20)
        recent_activity = [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_email": log.user.email if log.user else "Anonymous",
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "details_json": log.details_json,
                "created_at": log.created_at
            }
            for log in recent_logs
        ]

        return {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "total_interviews": total_interviews,
            "completed_interviews": completed_interviews,
            "average_readiness_score": round(float(avg_score), 1),
            "role_distribution": role_dist,
            "top_skill_gaps": top_gaps,
            "recent_activity": recent_activity
        }

    def list_users(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        users = self.user_repo.list_users(skip=skip, limit=limit)
        results = []
        for u in users:
            resumes_count = len(u.resumes)
            interviews_count = len(u.interviews)
            results.append({
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at,
                "resumes_count": resumes_count,
                "interviews_count": interviews_count
            })
        return results

    def toggle_user_active(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if user:
            user.is_active = not user.is_active
            self.db.commit()
            self.db.refresh(user)
        return user
