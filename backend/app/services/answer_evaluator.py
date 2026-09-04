import json
from typing import Dict, Any
from app.ai.gateway import get_ai_gateway
from app.ai.base import AIMessage


class AnswerEvaluator:
    """Answer evaluation service"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def evaluate_answer(
        self,
        question: Dict[str, Any],
        answer: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate interview answer with structured scoring"""

        prompt = f"""Evaluate this interview answer using a structured rubric.

Question: {question.get('question')}
Question Type: {question.get('type')}
Skill Being Tested: {question.get('skill')}
Difficulty: {question.get('difficulty')}

Candidate's Answer:
{answer}

Context:
- Candidate's claimed level in {question.get('skill')}: {context.get('claimed_level', 'Unknown')}

Evaluate on these dimensions (score each 0-10):
1. Correctness - Is the answer factually correct?
2. Technical Depth - How deep is the technical understanding?
3. Relevance - Does it directly address the question?
4. Clarity - Is the explanation clear and well-structured?
5. Problem Solving - Shows analytical thinking?

Return JSON:
{{
  "overall_score": float (0-10, average of dimension scores),
  "correctness_score": float (0-10),
  "technical_depth_score": float (0-10),
  "relevance_score": float (0-10),
  "clarity_score": float (0-10),
  "problem_solving_score": float (0-10),
  "strengths": ["specific strength 1", "specific strength 2"],
  "weaknesses": ["specific weakness 1", "specific weakness 2"],
  "evidence": ["concrete evidence from answer"],
  "skill_level_demonstrated": "beginner|intermediate|advanced|expert",
  "feedback": "Brief constructive feedback (2-3 sentences)",
  "should_followup": boolean,
  "followup_reason": "string or null"
}}

IMPORTANT:
- Be objective and evidence-based
- Use neutral language
- Base scores on actual answer content
- Don't assume knowledge not demonstrated
- Return ONLY valid JSON
"""

        messages = [
            AIMessage(role="system", content="You are an expert technical interviewer providing objective evaluations."),
            AIMessage(role="user", content=prompt)
        ]

        response = await self.ai_gateway.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )

        try:
            evaluation = json.loads(response.content)

            # Ensure overall_score is calculated correctly
            dimension_scores = [
                evaluation.get('correctness_score', 0),
                evaluation.get('technical_depth_score', 0),
                evaluation.get('relevance_score', 0),
                evaluation.get('clarity_score', 0),
                evaluation.get('problem_solving_score', 0)
            ]
            evaluation['overall_score'] = sum(dimension_scores) / len(dimension_scores)

            return evaluation
        except json.JSONDecodeError:
            content = response.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                evaluation = json.loads(content[start:end])
                return evaluation
            raise Exception("Failed to parse answer evaluation")


class FollowUpGenerator:
    """Follow-up question generator"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def generate_followup(
        self,
        original_question: Dict[str, Any],
        answer: str,
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate follow-up question based on answer"""

        prompt = f"""Generate a follow-up question to probe deeper.

Original Question: {original_question.get('question')}
Skill: {original_question.get('skill')}

Candidate's Answer: {answer}

Evaluation:
- Score: {evaluation.get('overall_score')}/10
- Demonstrated Level: {evaluation.get('skill_level_demonstrated')}
- Weaknesses: {json.dumps(evaluation.get('weaknesses', []))}

Generate a follow-up question that:
1. Probes deeper into the skill
2. Tests practical understanding
3. Addresses identified weak areas
4. Is appropriate for the demonstrated level

Return JSON:
{{
  "question": "The follow-up question text",
  "type": "{original_question.get('type')}",
  "difficulty": "beginner|intermediate|advanced",
  "skill": "{original_question.get('skill')}",
  "context": "Why this follow-up",
  "is_followup": true,
  "probing_aspect": "What specific aspect we're testing"
}}

Return ONLY valid JSON.
"""

        messages = [
            AIMessage(role="system", content="You are an expert interviewer generating strategic follow-up questions."),
            AIMessage(role="user", content=prompt)
        ]

        response = await self.ai_gateway.generate(
            messages=messages,
            temperature=0.6,
            max_tokens=400
        )

        try:
            followup = json.loads(response.content)
            return followup
        except json.JSONDecodeError:
            content = response.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            raise Exception("Failed to parse follow-up question")
