import json
from typing import Dict, Any, List, Optional
from app.ai.gateway import get_ai_gateway
from app.ai.base import AIMessage
from app.models import InterviewDifficulty


class InterviewPlanner:
    """Interview blueprint creation service"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def create_interview_blueprint(
        self,
        profile_data: Dict[str, Any],
        job_profile: Dict[str, Any],
        difficulty: str = "intermediate",
        total_questions: int = 15
    ) -> Dict[str, Any]:
        """Create an interview blueprint/plan"""

        prompt = f"""Create an interview plan for this candidate.

Candidate Profile Summary:
- Skills: {json.dumps(profile_data.get('skills', [])[:10])}
- Experience: {profile_data.get('total_experience_years', 0)} years
- Recent Projects: {json.dumps(profile_data.get('projects', [])[:3])}

Target Role: {job_profile.get('title')}
Required Skills: {json.dumps(job_profile.get('required_skills', []))}
Difficulty Level: {difficulty}
Total Questions: {total_questions}

Create an interview blueprint with question distribution:

Return JSON:
{{
  "difficulty": "{difficulty}",
  "total_questions": {total_questions},
  "distribution": {{
    "technical": {{
      "percentage": 30,
      "count": 5,
      "skills_to_test": ["skill1", "skill2"]
    }},
    "project": {{
      "percentage": 20,
      "count": 3,
      "focus": ["specific project aspects"]
    }},
    "problem_solving": {{
      "percentage": 20,
      "count": 3
    }},
    "behavioral": {{
      "percentage": 15,
      "count": 2
    }},
    "hr": {{
      "percentage": 10,
      "count": 2
    }},
    "role_specific": {{
      "percentage": 5,
      "count": 1
    }}
  }},
  "priority_skills": ["skill1", "skill2", "skill3"],
  "priority_projects": ["project1"],
  "adaptive_strategy": "Start with fundamentals, increase difficulty based on performance",
  "estimated_duration_minutes": 45
}}

Return ONLY valid JSON.
"""

        messages = [
            AIMessage(role="system", content="You are an expert technical interviewer."),
            AIMessage(role="user", content=prompt)
        ]

        response = await self.ai_gateway.generate(
            messages=messages,
            temperature=0.4,
            max_tokens=1000
        )

        try:
            blueprint = json.loads(response.content)
            return blueprint
        except json.JSONDecodeError:
            content = response.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            raise Exception("Failed to parse interview blueprint")


class QuestionGenerator:
    """Interview question generation service"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def generate_next_question(
        self,
        interview_context: Dict[str, Any],
        previous_questions: List[Dict[str, Any]],
        previous_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate the next interview question based on current state"""

        # Build context
        profile_summary = interview_context.get('profile_summary', {})
        job_title = interview_context.get('job_title', 'the role')
        blueprint = interview_context.get('blueprint', {})
        difficulty = interview_context.get('difficulty', 'intermediate')

        # Previous questions summary
        prev_q_summary = [
            f"Q{i+1} ({q.get('type')}): {q.get('skill')} - Score: {previous_evaluations[i].get('overall_score', 0) if i < len(previous_evaluations) else 'N/A'}"
            for i, q in enumerate(previous_questions[-5:])
        ]

        prompt = f"""Generate the next interview question.

Context:
- Role: {job_title}
- Difficulty: {difficulty}
- Questions asked: {len(previous_questions)}
- Candidate skills: {json.dumps(profile_summary.get('skills', [])[:10])}

Blueprint: {json.dumps(blueprint.get('distribution', {}))}

Previous Questions:
{chr(10).join(prev_q_summary) if prev_q_summary else 'None yet'}

Recent Performance Summary:
{self._get_performance_summary(previous_evaluations)}

Rules:
1. Do NOT repeat previous questions
2. Adjust difficulty based on performance
3. Test important skills from the blueprint
4. Mix question types appropriately
5. For follow-ups, probe deeper into weak areas

Return JSON:
{{
  "question": "The interview question text",
  "type": "technical|project|behavioral|hr|problem_solving|role_specific",
  "difficulty": "beginner|intermediate|advanced",
  "skill": "specific skill being tested",
  "context": "why this question",
  "is_followup": boolean,
  "parent_skill": "string if followup"
}}

Return ONLY valid JSON.
"""

        messages = [
            AIMessage(role="system", content="You are an expert technical interviewer generating adaptive questions."),
            AIMessage(role="user", content=prompt)
        ]

        response = await self.ai_gateway.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        try:
            question_data = json.loads(response.content)
            return question_data
        except json.JSONDecodeError:
            content = response.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            raise Exception("Failed to parse generated question")

    def _get_performance_summary(self, evaluations: List[Dict[str, Any]]) -> str:
        """Summarize recent performance"""
        if not evaluations:
            return "No evaluations yet"

        recent = evaluations[-3:]
        avg_score = sum(e.get('overall_score', 0) for e in recent) / len(recent) if recent else 0

        return f"Recent average score: {avg_score:.1f}/10. Last 3 questions performance trend."
