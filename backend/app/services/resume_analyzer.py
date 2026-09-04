import json
from typing import Dict, Any, List
from app.ai.gateway import get_ai_gateway
from app.ai.base import AIMessage


class ResumeAnalyzer:
    """AI-powered resume analysis service"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def extract_structured_profile(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured information from resume text"""

        prompt = f"""You are a professional resume parser. Extract structured information from the following resume text.

Return a valid JSON object with this exact structure:
{{
  "full_name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "summary": "string or null",
  "total_experience_years": float or null,
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "graduation_year": "string",
      "field_of_study": "string or null"
    }}
  ],
  "skills": [
    {{
      "name": "string",
      "category": "programming_language|framework|database|tool|soft_skill|other",
      "level": "beginner|intermediate|advanced|expert or null",
      "years": float or null
    }}
  ],
  "experiences": [
    {{
      "company": "string",
      "title": "string",
      "start_date": "string (YYYY-MM format)",
      "end_date": "string (YYYY-MM format) or 'Present'",
      "is_current": boolean,
      "description": "string or null",
      "responsibilities": ["string"]
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "technologies": ["string"],
      "role": "string or null",
      "duration": "string or null"
    }}
  ],
  "certifications": [
    {{
      "name": "string",
      "organization": "string or null",
      "issue_date": "string or null",
      "credential_id": "string or null"
    }}
  ]
}}

IMPORTANT:
- Return ONLY valid JSON, no markdown, no explanation
- Extract actual information from the resume
- Do not fabricate information
- Use null for missing fields
- Categorize skills accurately
- Estimate years of experience based on job dates if not explicitly stated

Resume Text:
{resume_text}
"""

        messages = [
            AIMessage(role="system", content="You are a professional resume parser that returns only valid JSON."),
            AIMessage(role="user", content=prompt)
        ]

        try:
            response = await self.ai_gateway.generate(
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )

            # Parse JSON response
            profile_data = json.loads(response.content)
            return profile_data

        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract JSON from response
            content = response.content
            # Try to find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                profile_data = json.loads(content[start:end])
                return profile_data
            raise Exception(f"Failed to parse AI response as JSON: {e}")

        except Exception as e:
            raise Exception(f"Resume analysis failed: {e}")


    async def analyze_resume_for_role(
        self,
        profile_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze resume match with job requirements"""

        prompt = f"""Analyze how well this candidate's profile matches the job requirements.

Candidate Profile:
{json.dumps(profile_data, indent=2)}

Job Requirements:
{json.dumps(job_requirements, indent=2)}

Return a JSON object with:
{{
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "weak_skills": ["skill5"],
  "relevant_experiences": ["experience description"],
  "relevant_projects": ["project description"],
  "overall_match_percentage": float (0-100),
  "readiness_level": "beginner|intermediate|advanced|expert",
  "recommended_focus_areas": ["area1", "area2"],
  "interview_topics": ["topic1", "topic2"]
}}

Return ONLY valid JSON.
"""

        messages = [
            AIMessage(role="system", content="You are an expert recruiter analyzing candidate-job fit."),
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
            raise Exception("Failed to parse resume-job match analysis")
