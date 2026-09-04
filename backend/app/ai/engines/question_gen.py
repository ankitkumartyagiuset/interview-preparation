import json
from typing import Dict, Any, List, Optional
from app.ai.gateway import ai_gateway
from app.ai.prompts.interview_prompts import INTERVIEW_QUESTION_SYSTEM_PROMPT, build_next_question_prompt
from app.ai.prompts.evaluation_prompts import FOLLOW_UP_SYSTEM_PROMPT, build_follow_up_prompt

class QuestionGeneratorEngine:
    """Generates context-aware, non-repetitive adaptive interview questions."""

    @staticmethod
    async def generate_next_question(
        candidate_summary: str,
        target_role: str,
        blueprint: Dict[str, Any],
        sequence_num: int,
        difficulty: str,
        previous_questions: List[str],
        previous_scores: List[float],
        current_skill_confidence: Dict[str, float],
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        prompt = build_next_question_prompt(
            candidate_summary=candidate_summary,
            target_role=target_role,
            blueprint=blueprint,
            sequence_num=sequence_num,
            difficulty=difficulty,
            previous_questions=previous_questions,
            previous_scores=previous_scores,
            current_skill_confidence=current_skill_confidence
        )
        return await ai_gateway.generate_json(
            prompt=prompt,
            system_prompt=INTERVIEW_QUESTION_SYSTEM_PROMPT,
            provider_name=provider_name
        )

question_generator_engine = QuestionGeneratorEngine()

class FollowUpGeneratorEngine:
    """Generates targeted follow-up questions when candidate answers warrant deeper inquiry."""

    @staticmethod
    async def evaluate_and_generate_follow_up(
        question_text: str,
        candidate_answer: str,
        target_skill: str,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        # Only trigger follow-up if answer is either brief (< 30 words) or mentions broad claims
        words = candidate_answer.strip().split()
        if len(words) < 5:
            # Too short for a meaningful follow-up, answer evaluator will flag as incomplete
            return {"should_follow_up": False}

        prompt = build_follow_up_prompt(question_text, candidate_answer, target_skill)
        return await ai_gateway.generate_json(
            prompt=prompt,
            system_prompt=FOLLOW_UP_SYSTEM_PROMPT,
            provider_name=provider_name
        )

follow_up_generator_engine = FollowUpGeneratorEngine()
