import json
from typing import List, Dict, Any

ROADMAP_SYSTEM_PROMPT = """You are a Principal Career Mentor and Staff Engineer.
Generate an actionable, realistic 7-day personalized skill gap improvement roadmap.

RULES:
1. Do NOT generate fake course URLs or broken links.
2. Provide concrete engineering concepts, hands-on practice exercises, mini-project specs, and mock interview questions.
3. Prioritize high-severity gaps where demonstrated skill level fell short of target requirements.

Return ONLY a valid JSON object:
{
  "title": "string",
  "duration_days": 7,
  "summary": "string",
  "overall_recommendation": "string",
  "items": [
    {
      "day_number": 1,
      "skill_name": "string",
      "current_level": "beginner|intermediate|advanced",
      "target_level": "intermediate|advanced",
      "priority": "low|medium|high",
      "concepts_json": ["string"],
      "practice_tasks_json": ["string"],
      "mini_project_json": {"title": "string", "description": "string"},
      "sample_questions_json": ["string"]
    }
  ]
}
"""

def build_roadmap_prompt(
    target_role: str,
    skill_gaps: List[Dict[str, Any]],
    overall_readiness: float
) -> str:
    return f"""Generate a 7-day personalized skill improvement roadmap for:
Target Role: {target_role}
Current Readiness Score: {overall_readiness}%

Detected Skill Gaps:
{json.dumps(skill_gaps, indent=2)}

Create a day-by-day 7-day curriculum addressing the highest priority gaps first, concluding with a full mock reassessment."""
