from typing import Dict, Any, Optional
from app.ai.gateway import ai_gateway
from app.ai.prompts.jd_prompts import JD_ANALYSIS_SYSTEM_PROMPT, build_jd_analysis_prompt

class JDAnalyzerEngine:
    """Analyzes job description text and extracts required/preferred competencies."""

    @staticmethod
    async def analyze_job_description(jd_text: str, role_title_hint: str = "", provider_name: Optional[str] = None) -> Dict[str, Any]:
        prompt = build_jd_analysis_prompt(jd_text, role_title_hint)
        return await ai_gateway.generate_json(
            prompt=prompt,
            system_prompt=JD_ANALYSIS_SYSTEM_PROMPT,
            provider_name=provider_name
        )

jd_analyzer_engine = JDAnalyzerEngine()

class InterviewPlannerEngine:
    """Plans interview blueprint and balances category weights."""

    @staticmethod
    def generate_default_blueprint(interview_type: str = "mixed", total_questions: int = 5) -> Dict[str, Any]:
        if interview_type == "technical":
            return {
                "technical_weight": 50,
                "project_weight": 25,
                "problem_solving_weight": 25,
                "communication_weight": 0,
                "behavioral_weight": 0,
                "role_specific_weight": 0,
                "total_questions": total_questions
            }
        elif interview_type == "behavioral":
            return {
                "technical_weight": 0,
                "project_weight": 20,
                "problem_solving_weight": 20,
                "communication_weight": 30,
                "behavioral_weight": 30,
                "role_specific_weight": 0,
                "total_questions": total_questions
            }
        elif interview_type == "project":
            return {
                "technical_weight": 20,
                "project_weight": 50,
                "problem_solving_weight": 20,
                "communication_weight": 10,
                "behavioral_weight": 0,
                "role_specific_weight": 0,
                "total_questions": total_questions
            }
        else:  # Mixed / Role-specific
            return {
                "technical_weight": 30,
                "project_weight": 20,
                "problem_solving_weight": 20,
                "communication_weight": 10,
                "behavioral_weight": 10,
                "role_specific_weight": 10,
                "total_questions": total_questions
            }

interview_planner_engine = InterviewPlannerEngine()
