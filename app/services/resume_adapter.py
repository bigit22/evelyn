import json
from typing import Any

from app.ai.client import AIClient
from app.ai.prompts import (
    RESUME_ADAPT_SYSTEM_PROMPT,
    build_resume_adapt_user_prompt,
)
from app.schemas.ai import ChatRequest, Message
from app.schemas.resume import AdaptedResume, ResumeAdaptRequest


class ResumeAdapterError(Exception):
    """Ошибка адаптации резюме."""


class ResumeAdapter:
    """Сервис для адаптации резюме под вакансию."""

    def __init__(self, ai_client: AIClient) -> None:
        self.ai = ai_client

    async def adapt(self, req: ResumeAdaptRequest) -> AdaptedResume:
        user_prompt = build_resume_adapt_user_prompt(
            base_resume=req.base_resume,
            vacancy_description=req.vacancy_description,
            target_role=req.target_role,
        )

        messages = [
            Message(role="system", content=RESUME_ADAPT_SYSTEM_PROMPT),
            Message(role="user", content=user_prompt),
        ]

        request = ChatRequest(messages=messages, temperature=0.4)
        raw_response = await self.ai.chat(request)

        return self._parse_ai_response(raw_response)

    def _parse_ai_response(self, raw_response: str) -> AdaptedResume:
        try:
            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.split("\n", 1)[1]
                clean_json = clean_json.rsplit("```", 1)[0].strip()

            data: dict[str, Any] = json.loads(clean_json)
        except json.JSONDecodeError as err:
            raise ResumeAdapterError(f"AI вернул невалидный JSON: {raw_response}") from err

        return AdaptedResume(
            summary=str(data.get("summary", "")),
            skills=[str(s) for s in data.get("skills", [])],
            adapted_experience=str(data.get("adapted_experience", "")),
            key_changes=[str(c) for c in data.get("key_changes", [])],
        )
