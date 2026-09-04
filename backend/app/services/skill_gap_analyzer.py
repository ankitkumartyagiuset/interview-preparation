import json
from typing import Dict, Any, List
from app.ai.gateway import get_ai_gateway
from app.ai.base import AIMessage


class SkillGapAnalyzer:
    """Skill gap detection and analysis service"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def analyze_skill_gaps(
        self,
        profile_skills: List[Dict[str, Any]],
        job_requirements: Dict[str, Any],
        interview_evaluations: List[Dict[str, Any]],
        questions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze skill gaps by comparing claimed vs demonstrated skills"""

        # Build skill performance map from interview
        skill_performance = self._build_skill_performance_map(questions, interview_evaluations)

        prompt = f"""Analyze skill gaps for this candidate.

Candidate's Resume Skills:
{json.dumps(profile_skills, indent=2)}

Job Required Skills:
{json.dumps(job_requirements.get('required_skills', []), indent=2)}

Interview Performance by Skill:
{json.dumps(skill_performance, indent=2)}

For each important skill, determine:
1. Required level for the job
2. Claimed level from resume
3. Demonstrated level in interview
4. Gap severity
5. Priority for improvement

Return JSON array:
[
  {{
    "skill": "skill name",
    "required_level": "beginner|intermediate|advanced|expert or null",
    "claimed_level": "beginner|intermediate|advanced|expert or null",
    "demonstrated_level": "beginner|intermediate|advanced|expert or null",
    "gap_severity": "none|low|medium|high",
    "priority": "low|medium|high",
    "confidence": float (0-1),
    "evidence": ["concrete evidence from interview"],
    "gap_analysis": "Brief explanation of the gap"
  }}
]

IMPORTANT:
- Use neutral language (avoid "dishonest" or "lying")
- Base analysis on actual interview performance
- Consider that nervousness can affect performance
- Only include skills that were actually tested or are job-critical
- Return ONLY valid JSON array
"""

        messages = [
            AIMessage(role="system", content="You are an objective skill assessment expert."),
            AIMessage(role="user", content=prompt)
        ]

        response = await self.ai_gateway.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )

        try:
            skill_gaps = json.loads(response.content)
            return skill_gaps if isinstance(skill_gaps, list) else []
        except json.JSONDecodeError:
            content = response.content
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                skill_gaps = json.loads(content[start:end])
                return skill_gaps
            raise Exception("Failed to parse skill gap analysis")

    def _build_skill_performance_map(
        self,
        questions: List[Dict[str, Any]],
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build a map of skill performance from interview"""
        skill_map = {}

        for i, question in enumerate(questions):
            skill = question.get('skill')
            if not skill or i >= len(evaluations):
                continue

            eval_data = evaluations[i]

            if skill not in skill_map:
                skill_map[skill] = {
                    "questions_asked": 0,
                    "average_score": 0,
                    "scores": [],
                    "demonstrated_level": None
                }

            skill_map[skill]["questions_asked"] += 1
            skill_map[skill]["scores"].append(eval_data.get('overall_score', 0))
            skill_map[skill]["average_score"] = sum(skill_map[skill]["scores"]) / len(skill_map[skill]["scores"])
            skill_map[skill]["demonstrated_level"] = eval_data.get('skill_level_demonstrated')

        return skill_map


class RoadmapGenerator:
    """Personalized learning roadmap generator"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def generate_roadmap(
        self,
        skill_gaps: List[Dict[str, Any]],
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized improvement roadmap"""

        # Focus on high-priority gaps
        priority_gaps = [
            gap for gap in skill_gaps
            if gap.get('priority') in ['high', 'medium'] and gap.get('gap_severity') in ['high', 'medium']
        ][:5]  # Top 5 priority gaps

        if not priority_gaps:
            return {
                "title": "No Critical Gaps Identified",
                "description": "Continue practicing and deepening existing skills",
                "estimated_duration_days": 0,
                "items": []
            }

        prompt = f"""Create a personalized learning roadmap to address these skill gaps.

Priority Skill Gaps:
{json.dumps(priority_gaps, indent=2)}

Candidate's Current Experience: {profile_data.get('total_experience_years', 0)} years

For each skill gap, create a structured learning plan with:
1. Concepts to learn (ordered by difficulty)
2. Practical exercises
3. Mini-project to solidify knowledge
4. Day-by-day breakdown

Return JSON:
{{
  "title": "Skill Development Roadmap",
  "description": "Overview of the learning path",
  "estimated_duration_days": integer (realistic timeframe),
  "items": [
    {{
      "skill": "skill name",
      "current_level": "beginner|intermediate|advanced|expert",
      "target_level": "beginner|intermediate|advanced|expert",
      "priority": "high|medium|low",
      "day_number": integer (which day to focus on this),
      "concepts_to_learn": ["concept1", "concept2", "concept3"],
      "practice_tasks": ["task1", "task2"],
      "mini_project": "A small project description to apply the skill",
      "resources": [
        {{"title": "Resource name", "type": "documentation|tutorial|practice|video"}}
      ]
    }}
  ]
}}

IMPORTANT:
- Be realistic about timeframes
- Order items by logical progression
- Make tasks specific and actionable
- Don't include fake URLs or specific course names
- Return ONLY valid JSON
"""

        messages = [
            AIMessage(role="system", content="You are a learning path designer creating practical skill development plans."),
            AIMessage(role="user", content=prompt)
        ]

        response = await self.ai_gateway.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=2000
        )

        try:
            roadmap = json.loads(response.content)
            return roadmap
        except json.JSONDecodeError:
            content = response.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            raise Exception("Failed to parse roadmap")
