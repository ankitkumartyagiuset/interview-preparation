import pytest
from app.ai.gateway import AIGateway
from app.ai.base import AIMessage


@pytest.mark.asyncio
async def test_ai_gateway_mock_provider():
    """Test AI Gateway with mock provider"""
    gateway = AIGateway(provider_name="mock")

    assert gateway.validate_config()

    messages = [
        AIMessage(role="system", content="You are a helpful assistant"),
        AIMessage(role="user", content="Parse this resume")
    ]

    response = await gateway.generate(messages, temperature=0.5, max_tokens=500)

    assert response is not None
    assert response.content is not None
    assert response.model == "mock-model"
    assert isinstance(response.content, str)


@pytest.mark.asyncio
async def test_mock_provider_resume_parsing():
    """Test mock provider resume parsing response"""
    gateway = AIGateway(provider_name="mock")

    messages = [
        AIMessage(role="user", content="Parse this resume and extract skills")
    ]

    response = await gateway.generate(messages)

    assert "python" in response.content.lower() or "skills" in response.content.lower()


@pytest.mark.asyncio
async def test_mock_provider_question_generation():
    """Test mock provider question generation"""
    gateway = AIGateway(provider_name="mock")

    messages = [
        AIMessage(role="user", content="Generate an interview question about Python")
    ]

    response = await gateway.generate(messages)

    assert "question" in response.content.lower() or "?" in response.content
