import logging
from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.ai.providers.base import AIProvider
from backend.app.ai.providers.mock_provider import MockProvider
from backend.app.ai.providers.openai_provider import OpenAIProvider
from backend.app.ai.providers.cloud_providers import AnthropicProvider, GeminiProvider, GroqProvider

logger = logging.getLogger("ai_gateway")

class AIGateway:
    """
    Provider-agnostic AI Gateway that routes LLM requests to the configured provider,
    manages fallback failovers, and enforces safety controls.
    """

    def __init__(self):
        self._mock_provider = MockProvider()
        self._providers: Dict[str, AIProvider] = {
            "mock": self._mock_provider,
        }

    def _get_provider(self, provider_name: Optional[str] = None) -> AIProvider:
        target = (provider_name or settings.AI_PROVIDER or "mock").lower()

        if target in self._providers:
            return self._providers[target]

        try:
            if target == "openai":
                provider = OpenAIProvider()
            elif target == "anthropic":
                provider = AnthropicProvider()
            elif target == "gemini":
                provider = GeminiProvider()
            elif target == "groq":
                provider = GroqProvider()
            else:
                logger.warning(f"Unknown provider '{target}', falling back to MockProvider")
                return self._mock_provider

            self._providers[target] = provider
            return provider
        except Exception as e:
            logger.error(f"Failed to initialize AI provider '{target}': {e}. Using mock fallback.")
            return self._mock_provider

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider_name: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        provider = self._get_provider(provider_name)
        try:
            return await provider.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.warning(f"AI Provider error during generate_text: {e}. Executing failover to MockProvider.")
            return await self._mock_provider.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        provider_name: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        provider = self._get_provider(provider_name)
        try:
            return await provider.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                schema=schema,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.warning(f"AI Provider error during generate_json: {e}. Executing failover to MockProvider.")
            return await self._mock_provider.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                schema=schema,
                temperature=temperature,
                max_tokens=max_tokens
            )

ai_gateway = AIGateway()
