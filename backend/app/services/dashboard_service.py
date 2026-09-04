from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.repositories.interview_repo import InterviewRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.user_repo import UserRepository
from app.models.user import User

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.interview_repo = InterviewRepository(db)
        self.report_repo = ReportRepository(db)
        self.user_repo = UserRepository(db)

    def get_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        user = self.user_repo.get_by_id(user_id)
        interviews = self.interview_repo.list_by_user(user_id)
        
        completed = [i for i in interviews if i.status == "completed"]
        total_count = len(interviews)
        completed_count = len(completed)

        # Average readiness score across completed interviews
        if completed:
            overall_readiness = round(sum(i.overall_score or 0 for i in completed) / len(completed), 1)
        else:
            overall_readiness = 0.0

        if overall_readiness >= 75:
            readiness_band = "Interview Ready"
        elif overall_readiness >= 60:
            readiness_band = "Developing"
        elif overall_readiness > 0:
            readiness_band = "Beginner"
        else:
            readiness_band = "Not Started"

        # Aggregated Category Scores
        cat_averages = {
            "technical": 0.0,
            "projects": 0.0,
            "problem_solving": 0.0,
            "communication": 0.0,
            "hr_behavioral": 0.0
        }

        all_strengths = []
        recent_interviews_list = []
        progress_trend = []

        # Pull reports from completed interviews
        reports = []
        for i in completed:
            r = self.report_repo.get_report_by_interview(i.id, user_id=user_id)
            if r:
                reports.append(r)

        if reports:
            cat_averages["technical"] = round(sum(r.technical_score for r in reports) / len(reports), 1)
            cat_averages["projects"] = round(sum(r.project_score for r in reports) / len(reports), 1)
            cat_averages["problem_solving"] = round(sum(r.problem_solving_score for r in reports) / len(reports), 1)
            cat_averages["communication"] = round(sum(r.communication_score for r in reports) / len(reports), 1)
            cat_averages["hr_behavioral"] = round(sum(r.hr_score for r in reports) / len(reports), 1)
            
            for r in reports:
                all_strengths.extend(r.strengths_json or [])
        else:
            # Defaults for zero state
            cat_averages = {
                "technical": 70.0,
                "projects": 72.0,
                "problem_solving": 65.0,
                "communication": 75.0,
                "hr_behavioral": 70.0
            }

        # Progress trend list (chronological order)
        for i in reversed(completed):
            rep = self.report_repo.get_report_by_interview(i.id, user_id=user_id)
            progress_trend.append({
                "interview_id": i.id,
                "interview_title": i.title,
                "date": i.completed_at.strftime("%b %d") if i.completed_at else i.created_at.strftime("%b %d"),
                "overall_score": i.overall_score or 0.0,
                "technical_score": rep.technical_score if rep else (i.overall_score or 0.0),
                "communication_score": rep.communication_score if rep else 75.0,
                "problem_solving_score": rep.problem_solving_score if rep else 70.0
            })

        # Recent interviews
        for i in interviews[:5]:
            recent_interviews_list.append({
                "id": i.id,
                "title": i.title,
                "status": i.status,
                "difficulty": i.difficulty,
                "overall_score": i.overall_score,
                "created_at": i.created_at.strftime("%Y-%m-%d %H:%M")
            })

        # Priority gaps
        user_gaps = self.report_repo.get_skill_gaps_by_user(user_id)
        priority_gaps = []
        for g in user_gaps[:4]:
            priority_gaps.append({
                "skill_name": g.skill_name,
                "required_level": g.required_level,
                "claimed_level": g.claimed_level,
                "demonstrated_level": g.demonstrated_level,
                "gap_severity": g.gap_severity,
                "priority": g.priority
            })

        # Active roadmap
        latest_roadmap = self.report_repo.get_latest_roadmap_by_user(user_id)
        active_roadmap_data = None
        if latest_roadmap:
            items_data = [
                {
                    "id": it.id,
                    "day_number": it.day_number,
                    "skill_name": it.skill_name,
                    "is_completed": it.is_completed
                }
                for it in latest_roadmap.items
            ]
            completed_days = sum(1 for it in latest_roadmap.items if it.is_completed)
            active_roadmap_data = {
                "id": latest_roadmap.id,
                "title": latest_roadmap.title,
                "duration_days": latest_roadmap.duration_days,
                "completed_days": completed_days,
                "progress_percent": round((completed_days / (latest_roadmap.duration_days or 1)) * 100, 1),
                "items": items_data
            }

        top_strengths = list(dict.fromkeys(all_strengths))[:4] if all_strengths else [
            "Strong foundation in REST APIs & Python",
            "Clear technical problem breakdown",
            "Structured communication approach"
        ]

        return {
            "user_name": user.full_name if user else "Candidate",
            "total_interviews": total_count,
            "completed_interviews": completed_count,
            "overall_readiness": overall_readiness,
            "readiness_band": readiness_band,
            "category_averages": cat_averages,
            "top_strengths": top_strengths,
            "priority_gaps": priority_gaps,
            "recent_interviews": recent_interviews_list,
            "progress_trend": progress_trend,
            "active_roadmap": active_roadmap_data
        }
