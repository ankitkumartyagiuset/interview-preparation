import json
from typing import List, Dict, Any

INTERVIEW_QUESTION_SYSTEM_PROMPT = """You are an elite, adaptive Technical and Behavioral Interviewer.
Your goal is to conduct a professional, rigorous, and personalized competency interview.

RULES:
1. Always base questions on the candidate's actual resume claims, projects, and target role requirements.
2. Formulate realistic, scenario-based questions that test genuine depth rather than rote memorization.
3. NEVER repeat a question that was previously asked in this session.
4. Adapt difficulty dynamically based on previous answer scores and confidence.
5. Do NOT include hidden reasoning or evaluation hints in the question text.

Return ONLY a valid JSON object matching:
{
  "sequence_num": 1,
  "category": "technical|project|problem_solving|communication|behavioral|role_specific",
  "target_skill": "string",
  "difficulty": "beginner|intermediate|advanced|expert",
  "question_text": "string",
  "context_rationale": "string",
  "is_follow_up": false
}
"""

def build_next_question_prompt(
    candidate_summary: str,
    target_role: str,
    blueprint: Dict[str, Any],
    sequence_num: int,
    difficulty: str,
    previous_questions: List[str],
    previous_scores: List[float],
    current_skill_confidence: Dict[str, float]
) -> str:
    return f"""Generate the next interview question for sequence: {sequence_num}.

Target Role / JD: {target_role}
Current Difficulty Tier: {difficulty}
Interview Blueprint Weights: {json.dumps(blueprint)}

Candidate Background:
{candidate_summary}

Previous Questions Asked in this Interview (DO NOT REPEAT):
{json.dumps(previous_questions, indent=2)}

Previous Answer Scores: {previous_scores}
Current Skill Confidence: {json.dumps(current_skill_confidence)}

Formulate the next most valuable question to assess readiness and validate resume claims."""
