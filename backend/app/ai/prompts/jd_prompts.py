JD_ANALYSIS_SYSTEM_PROMPT = """You are a Principal Talent Architect and Technical Hiring Manager.
Analyze the provided Job Description text and extract structured competency requirements.

Return ONLY a valid JSON object matching this schema:
{
  "title": "string",
  "seniority": "junior|intermediate|senior|lead",
  "experience_years_required": 2.0,
  "required_skills_json": [
    {"name": "string", "level": "beginner|intermediate|advanced|expert", "category": "string"}
  ],
  "preferred_skills_json": [
    {"name": "string", "level": "beginner|intermediate|advanced|expert", "category": "string"}
  ],
  "responsibilities_json": [
    "string"
  ]
}
"""

def build_jd_analysis_prompt(jd_text: str, role_title_hint: str = "") -> str:
    return f"""Analyze the following job description and extract competency requirements:
Job Role Hint: {role_title_hint}

--- JOB DESCRIPTION START ---
{jd_text[:5000]}
--- JOB DESCRIPTION END ---

Provide the structured JSON output with required vs preferred skills, expected seniority, and key responsibilities."""
