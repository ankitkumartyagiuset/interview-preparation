from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.skill_gap import SkillGap, Roadmap, RoadmapItem
from backend.app.models.report import Report

class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_skill_gaps(self, interview_id: int, user_id: int, gaps: List[Dict[str, Any]]) -> List[SkillGap]:
        created_gaps = []
        for g in gaps:
            gap = SkillGap(
                interview_id=interview_id,
                user_id=user_id,
                skill_name=g.get("skill_name"),
                category=g.get("category", "technical"),
                required_level=g.get("required_level", "intermediate"),
                claimed_level=g.get("claimed_level", "intermediate"),
                demonstrated_level=g.get("demonstrated_level", "beginner"),
                gap_severity=g.get("gap_severity", "medium"),
                priority=g.get("priority", "medium"),
                confidence_score=g.get("confidence_score", 0.8),
                evidence_notes=g.get("evidence_notes")
            )
            self.db.add(gap)
            created_gaps.append(gap)
        self.db.commit()
        return created_gaps

    def get_skill_gaps_by_interview(self, interview_id: int) -> List[SkillGap]:
        return self.db.query(SkillGap).filter(SkillGap.interview_id == interview_id).all()

    def get_skill_gaps_by_user(self, user_id: int) -> List[SkillGap]:
        return self.db.query(SkillGap).filter(SkillGap.user_id == user_id).order_by(SkillGap.created_at.desc()).all()

    def save_roadmap(
        self,
        interview_id: int,
        user_id: int,
        title: str,
        duration_days: int,
        summary: str,
        overall_recommendation: str,
        items: List[Dict[str, Any]]
    ) -> Roadmap:
        roadmap = Roadmap(
            interview_id=interview_id,
            user_id=user_id,
            title=title,
            duration_days=duration_days,
            summary=summary,
            overall_recommendation=overall_recommendation
        )
        self.db.add(roadmap)
        self.db.flush()

        for itm in items:
            ritem = RoadmapItem(
                roadmap_id=roadmap.id,
                day_number=itm.get("day_number", 1),
                skill_name=itm.get("skill_name", ""),
                current_level=itm.get("current_level", "beginner"),
                target_level=itm.get("target_level", "intermediate"),
                priority=itm.get("priority", "high"),
                concepts_json=itm.get("concepts_json", []),
                practice_tasks_json=itm.get("practice_tasks_json", []),
                mini_project_json=itm.get("mini_project_json", {}),
                sample_questions_json=itm.get("sample_questions_json", []),
                is_completed=False
            )
            self.db.add(ritem)

        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def get_roadmap_by_interview(self, interview_id: int) -> Optional[Roadmap]:
        return self.db.query(Roadmap).filter(Roadmap.interview_id == interview_id).first()

    def get_latest_roadmap_by_user(self, user_id: int) -> Optional[Roadmap]:
        return self.db.query(Roadmap).filter(Roadmap.user_id == user_id).order_by(Roadmap.created_at.desc()).first()

    def toggle_roadmap_item(self, item_id: int) -> Optional[RoadmapItem]:
        item = self.db.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
        if item:
            item.is_completed = not item.is_completed
            self.db.commit()
            self.db.refresh(item)
        return item

    def save_report(
        self,
        interview_id: int,
        user_id: int,
        report_data: Dict[str, Any]
    ) -> Report:
        report = Report(
            interview_id=interview_id,
            user_id=user_id,
            overall_readiness_score=report_data.get("overall_readiness_score", 0.0),
            readiness_band=report_data.get("readiness_band", "Developing"),
            technical_score=report_data.get("technical_score", 0.0),
            project_score=report_data.get("project_score", 0.0),
            problem_solving_score=report_data.get("problem_solving_score", 0.0),
            communication_score=report_data.get("communication_score", 0.0),
            hr_score=report_data.get("hr_score", 0.0),
            role_specific_score=report_data.get("role_specific_score", 0.0),
            strengths_json=report_data.get("strengths_json", []),
            weaknesses_json=report_data.get("weaknesses_json", []),
            verified_claims_json=report_data.get("verified_claims_json", []),
            summary=report_data.get("summary"),
            recommendation=report_data.get("recommendation"),
            disclaimer=report_data.get("disclaimer", "This assessment is an interview-preparation/readiness assessment and is not a definitive hiring decision.")
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report_by_interview(self, interview_id: int, user_id: Optional[int] = None) -> Optional[Report]:
        query = self.db.query(Report).filter(Report.interview_id == interview_id)
        if user_id:
            query = query.filter(Report.user_id == user_id)
        return query.first()
