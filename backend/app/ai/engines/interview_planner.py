from typing import Dict, Any

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
