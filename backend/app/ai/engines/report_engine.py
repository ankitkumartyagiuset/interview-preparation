from typing import List, Dict, Any, Optional
from backend.app.ai.gateway import ai_gateway

class ReportEngine:
    """Aggregates all evaluation metrics, computes readiness bands, and creates final candidate report."""

    @staticmethod
    def calculate_readiness_band(score: float) -> str:
        if score >= 90:
            return "Highly Ready"
        elif score >= 75:
            return "Interview Ready"
        elif score >= 60:
            return "Developing"
        elif score >= 40:
            return "Beginner"
        else:
            return "Not Ready"

    @staticmethod
    async def generate_final_report(
        candidate_name: str,
        target_role: str,
        evaluations: List[Dict[str, Any]],
        skill_gaps: List[Dict[str, Any]],
        blueprint: Dict[str, Any],
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        # Aggregate scores by category
        cat_scores: Dict[str, List[float]] = {
            "technical": [],
            "project": [],
            "problem_solving": [],
            "communication": [],
            "behavioral": [],
            "role_specific": []
        }

        all_strengths = []
        all_weaknesses = []

        for ev in evaluations:
            cat = ev.get("category", "technical")
            score = ev.get("score", 7.0) * 10.0  # Scale to 0-100
            
            if cat in cat_scores:
                cat_scores[cat].append(score)
            else:
                cat_scores["technical"].append(score)
                
            all_strengths.extend(ev.get("strengths_json", []))
            all_weaknesses.extend(ev.get("weaknesses_json", []))

        # Calculate category averages (default to baseline 75.0 if category was unasked)
        def avg(lst, default=75.0):
            return round(sum(lst) / len(lst), 1) if lst else default

        technical_score = avg(cat_scores["technical"], 80.0)
        project_score = avg(cat_scores["project"], 78.0)
        problem_solving_score = avg(cat_scores["problem_solving"], 75.0)
        communication_score = avg(cat_scores["communication"], 82.0)
        hr_score = avg(cat_scores["behavioral"], 80.0)
        role_specific_score = avg(cat_scores["role_specific"], 78.0)

        # Weighted Overall Score
        overall_readiness = round(
            (technical_score * 0.30) +
            (project_score * 0.20) +
            (problem_solving_score * 0.20) +
            (communication_score * 0.10) +
            (hr_score * 0.10) +
            (role_specific_score * 0.10),
            1
        )
        readiness_band = ReportEngine.calculate_readiness_band(overall_readiness)

        # Verified claims summary
        verified_claims = []
        for gap in skill_gaps[:6]:
            cl = gap.get("claimed_level", "intermediate")
            dm = gap.get("demonstrated_level", "intermediate")
            if cl == dm:
                verdict = "Validated Match"
            elif cl == "expert" and dm == "intermediate":
                verdict = "Partial Match (Needs Practice)"
            elif cl == "advanced" and dm == "beginner":
                verdict = "Significant Gap"
            else:
                verdict = "Demonstrated Competency"

            verified_claims.append({
                "skill": gap.get("skill_name"),
                "claimed_level": cl,
                "demonstrated_level": dm,
                "verdict": verdict
            })

        # Deduplicate strengths & weaknesses
        top_strengths = list(dict.fromkeys(all_strengths))[:4]
        if not top_strengths:
            top_strengths = [
                "Clear conceptual grounding in core architecture principles",
                "Strong alignment with target role technical prerequisites",
                "Concise and professional response structuring"
            ]

        top_weaknesses = list(dict.fromkeys(all_weaknesses))[:3]
        if not top_weaknesses:
            top_weaknesses = [
                "Could provide deeper concrete edge-case analysis in high-throughput scenarios",
                "Opportunity to reinforce database indexing internals"
            ]

        summary = (
            f"{candidate_name} completed the competency interview for {target_role} with an overall readiness score of {overall_readiness}% ({readiness_band}). "
            f"Demonstrated solid proficiency in technical problem solving and project articulation."
        )

        recommendation = (
            f"Candidate is classified as '{readiness_band}'. Recommended to review the customized 7-day practice roadmap, "
            f"focusing on highlighted high-priority skill gaps before final on-site assessment."
        )

        return {
            "overall_readiness_score": overall_readiness,
            "readiness_band": readiness_band,
            "technical_score": technical_score,
            "project_score": project_score,
            "problem_solving_score": problem_solving_score,
            "communication_score": communication_score,
            "hr_score": hr_score,
            "role_specific_score": role_specific_score,
            "strengths_json": top_strengths,
            "weaknesses_json": top_weaknesses,
            "verified_claims_json": verified_claims,
            "summary": summary,
            "recommendation": recommendation,
            "disclaimer": "This assessment is an interview-preparation/readiness assessment and is not a definitive hiring decision."
        }

report_engine = ReportEngine()
