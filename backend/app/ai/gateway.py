import json
from typing import Any, Dict, List, Optional
from app.ai.base import AIProvider, AIMessage, AIResponse, AIProviderError
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.mock_provider import MockProvider
from app.core.config import settings


class AIGateway:
    """Provider-independent AI Gateway"""

    def __init__(self, provider_name: Optional[str] = None):
        self.provider_name = provider_name or settings.AI_PROVIDER
        self.provider = self._get_provider()

    def _get_provider(self) -> AIProvider:
        """Get AI provider instance"""
        if self.provider_name == "openai":
            return OpenAIProvider()
        elif self.provider_name == "anthropic":
            return AnthropicProvider()
        elif self.provider_name == "mock":
            return MockProvider()
        else:
            raise AIProviderError(f"Unknown provider: {self.provider_name}")

    async def generate(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate AI response through the configured provider"""
        try:
            return await self.provider.generate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        except Exception as e:
            raise AIProviderError(f"AI generation failed: {str(e)}")

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str,
        provider_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        gateway = self if not provider_name or provider_name == self.provider_name else AIGateway(provider_name)
        response = await gateway.generate([
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=prompt),
        ])
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise AIProviderError("AI provider returned invalid JSON") from exc

    def validate_config(self) -> bool:
        """Validate current provider configuration"""
        return self.provider.validate_config()


# Singleton instance
_gateway: Optional[AIGateway] = None


def get_ai_gateway() -> AIGateway:
    """Get AI Gateway singleton"""
    global _gateway
    if _gateway is None:
        _gateway = AIGateway()
    return _gateway


ai_gateway = get_ai_gateway()
