from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class AIMessage(BaseModel):
    """Standardized AI message format"""
    role: str  # system, user, assistant
    content: str


class AIResponse(BaseModel):
    """Standardized AI response format"""
    content: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs

    @abstractmethod
    async def generate(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate AI response"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration"""
        pass


class AIProviderError(Exception):
    """AI Provider specific error"""
    pass
