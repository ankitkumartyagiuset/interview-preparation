import json
from typing import Dict, Any
from app.ai.gateway import get_ai_gateway
from app.ai.base import AIMessage


class JobDescriptionAnalyzer:
    """Job description analysis service"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Extract structured requirements from job description"""

        prompt = f"""Analyze this job description and extract structured information.

Return a valid JSON object with this exact structure:
{{
  "title": "string",
  "experience_level": "string (e.g., 'Junior (0-2 years)', 'Mid-level (3-5 years)', 'Senior (5+ years)')",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3", "skill4"],
  "technical_requirements": ["requirement1", "requirement2"],
  "soft_skills": ["communication", "teamwork"],
  "responsibilities": ["responsibility1", "responsibility2"],
  "key_focus_areas": ["area1", "area2"],
  "tools_and_technologies": ["tool1", "tool2"],
  "education_requirements": "string or null",
  "certifications": ["cert1"] or null
}}

IMPORTANT:
- Return ONLY valid JSON
- Be specific about skills
- Distinguish between required and preferred
- Extract actual requirements, don't fabricate

Job Description:
{jd_text}
"""

        messages = [
            AIMessage(role="system", content="You are an expert recruiter analyzing job descriptions."),
            AIMessage(role="user", content=prompt)
        ]

        response = await self.ai_gateway.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )

        try:
            analysis = json.loads(response.content)
            return analysis
        except json.JSONDecodeError:
            content = response.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            raise Exception("Failed to parse JD analysis")

    def create_job_profile_from_role(self, job_role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create job profile from predefined job role"""
        return {
            "title": job_role_data.get("title"),
            "experience_level": job_role_data.get("experience_level"),
            "required_skills": job_role_data.get("required_skills", []),
            "preferred_skills": job_role_data.get("preferred_skills", []),
            "responsibilities": job_role_data.get("responsibilities", []),
            "technical_requirements": job_role_data.get("required_skills", []),
            "key_focus_areas": [],
            "tools_and_technologies": []
        }
