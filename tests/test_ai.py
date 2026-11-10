import pytest
from pydantic import ValidationError

from app.ai.client import AIClient, InvalidAPIKeyError
from app.schemas.ai import ChatRequest, Message


class TestAIClientInit:
    """Тесты создания клиента."""

    def test_rejects_empty_key(self) -> None:
        with pytest.raises(InvalidAPIKeyError):
            AIClient(provider="openrouter", api_key="")

    def test_rejects_unknown_provider(self) -> None:
        with pytest.raises(ValueError, match="Неизвестный провайдер"):
            AIClient(provider="banana", api_key="sk-test")

    def test_creates_openrouter_client(self) -> None:
        client = AIClient(provider="openrouter", api_key="sk-test")
        assert client.provider == "openrouter"
        assert "openrouter" in client.base_url

    def test_creates_gemini_client(self) -> None:
        client = AIClient(provider="gemini", api_key="AIza-test")
        assert client.provider == "gemini"
        assert "googleapis" in client.base_url


class TestChatRequest:
    """Тесты схем."""

    def test_default_values(self) -> None:
        msg = Message(role="user", content="Привет")
        req = ChatRequest(messages=[msg])
        assert req.temperature == 0.7
        assert "gemini" in req.model

    def test_rejects_invalid_role(self) -> None:
        with pytest.raises(ValidationError):  # Pydantic ValidationError
            Message(role="banana", content="test")  # type: ignore[arg-type]
