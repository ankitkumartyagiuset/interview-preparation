from typing import List, Dict, Any, Optional
from backend.app.ai.gateway import ai_gateway
from backend.app.ai.prompts.roadmap_prompts import ROADMAP_SYSTEM_PROMPT, build_roadmap_prompt

class RoadmapEngine:
    """Generates 7-day personalized skill gap remediation plans."""

    @staticmethod
    async def generate_roadmap(
        target_role: str,
        skill_gaps: List[Dict[str, Any]],
        overall_readiness: float,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        prompt = build_roadmap_prompt(
            target_role=target_role,
            skill_gaps=skill_gaps,
            overall_readiness=overall_readiness
        )
        return await ai_gateway.generate_json(
            prompt=prompt,
            system_prompt=ROADMAP_SYSTEM_PROMPT,
            provider_name=provider_name
        )

roadmap_engine = RoadmapEngine()
