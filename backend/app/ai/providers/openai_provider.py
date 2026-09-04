from typing import List, Optional
import openai
from app.ai.base import AIProvider, AIMessage, AIResponse, AIProviderError
from app.core.config import settings


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        super().__init__(
            api_key=api_key or settings.OPENAI_API_KEY,
            model=model or settings.OPENAI_MODEL,
            **kwargs
        )
        if self.api_key:
            openai.api_key = self.api_key

    def validate_config(self) -> bool:
        """Validate OpenAI configuration"""
        return bool(self.api_key and self.model)

    async def generate(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate response using OpenAI"""
        if not self.validate_config():
            raise AIProviderError("OpenAI API key not configured")

        try:
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            return AIResponse(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                raw_response=response.to_dict()
            )

        except openai.error.OpenAIError as e:
            raise AIProviderError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise AIProviderError(f"Unexpected error: {str(e)}")
