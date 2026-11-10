from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    """Одно сообщение в диалоге с AI."""

    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """Запрос к AI-клиенту."""

    messages: list[Message]
    model: str = "google/gemini-2.5-flash-preview"
    temperature: float = 0.7
