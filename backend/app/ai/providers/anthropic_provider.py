from typing import List, Optional
import anthropic
from app.ai.base import AIProvider, AIMessage, AIResponse, AIProviderError
from app.core.config import settings


class AnthropicProvider(AIProvider):
    """Anthropic provider implementation"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        super().__init__(
            api_key=api_key or settings.ANTHROPIC_API_KEY,
            model=model or settings.ANTHROPIC_MODEL,
            **kwargs
        )
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def validate_config(self) -> bool:
        """Validate Anthropic configuration"""
        return bool(self.api_key and self.model and self.client)

    async def generate(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate response using Anthropic"""
        if not self.validate_config():
            raise AIProviderError("Anthropic API key not configured")

        try:
            # Separate system message from user messages
            system_message = ""
            user_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    user_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                system=system_message if system_message else None,
                messages=user_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            return AIResponse(
                content=response.content[0].text,
                model=response.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                raw_response={"id": response.id, "type": response.type}
            )

        except anthropic.APIError as e:
            raise AIProviderError(f"Anthropic API error: {str(e)}")
        except Exception as e:
            raise AIProviderError(f"Unexpected error: {str(e)}")
