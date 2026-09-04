from typing import Dict, Any, Optional
from app.ai.gateway import ai_gateway
from app.ai.prompts.evaluation_prompts import EVALUATION_SYSTEM_PROMPT, build_answer_evaluation_prompt

class AnswerEvaluatorEngine:
    """Evaluates candidate answers against multi-dimensional rubrics and extracts evidence citations."""

    @staticmethod
    async def evaluate_answer(
        question_text: str,
        target_skill: str,
        claimed_level: str,
        candidate_answer: str,
        target_role: str,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        prompt = build_answer_evaluation_prompt(
            question_text=question_text,
            target_skill=target_skill,
            claimed_level=claimed_level,
            candidate_answer=candidate_answer,
            target_role=target_role
        )
        return await ai_gateway.generate_json(
            prompt=prompt,
            system_prompt=EVALUATION_SYSTEM_PROMPT,
            provider_name=provider_name
        )

answer_evaluator_engine = AnswerEvaluatorEngine()
