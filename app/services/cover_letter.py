import json
from typing import Any

from app.ai.client import AIClient
from app.ai.prompts import (
    COVER_LETTER_SYSTEM_PROMPT,
    build_cover_letter_user_prompt,
)
from app.schemas.ai import ChatRequest, Message
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse


class CoverLetterError(Exception):
    """Ошибка генерации сопроводительного письма."""


class CoverLetterGenerator:
    """Сервис генерации сопроводительных писем."""

    def __init__(self, ai_client: AIClient) -> None:
        self.ai = ai_client

    async def generate(self, req: CoverLetterRequest) -> CoverLetterResponse:
        user_prompt = build_cover_letter_user_prompt(
            resume=req.resume,
            vacancy_description=req.vacancy_description,
            company_name=req.company_name,
            company_info=req.company_info,
        )

        messages = [
            Message(role="system", content=COVER_LETTER_SYSTEM_PROMPT),
            Message(role="user", content=user_prompt),
        ]

        request = ChatRequest(messages=messages, temperature=0.6)
        raw_response = await self.ai.chat(request)

        return self._parse_ai_response(raw_response)

    def _parse_ai_response(self, raw_response: str) -> CoverLetterResponse:
        try:
            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.split("\n", 1)[1]
                clean_json = clean_json.rsplit("```", 1)[0].strip()

            data: dict[str, Any] = json.loads(clean_json)
        except json.JSONDecodeError as err:
            raise CoverLetterError(f"AI вернул невалидный JSON: {raw_response}") from err

        return CoverLetterResponse(
            cover_letter=str(data.get("cover_letter", "")),
            key_highlights=[str(h) for s in data.get("key_highlights", []) for h in [s]],
        )
