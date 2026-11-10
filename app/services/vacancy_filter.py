import json
from typing import Any

from app.ai.client import AIClient
from app.ai.prompts import FILTER_SYSTEM_PROMPT, build_filter_user_prompt
from app.schemas.ai import ChatRequest, Message
from app.schemas.vacancy import EvaluatedVacancy, Vacancy


class VacancyFilterError(Exception):
    """Ошибка фильтрации вакансий."""


class VacancyFilter:
    """Фильтрация вакансий с помощью AI."""

    def __init__(self, ai_client: AIClient) -> None:
        self.ai = ai_client

    async def evaluate_vacancies(
        self, profile: str, vacancies: list[Vacancy]
    ) -> list[EvaluatedVacancy]:
        if not vacancies:
            return []

        # Формируем компактное текстовое представление вакансий для промпта
        vacancies_text = self._format_vacancies(vacancies)
        user_prompt = build_filter_user_prompt(profile, vacancies_text)

        messages = [
            Message(role="system", content=FILTER_SYSTEM_PROMPT),
            Message(role="user", content=user_prompt),
        ]

        # Для JSON-анализа ставим низкую температуру
        request = ChatRequest(messages=messages, temperature=0.2)
        raw_response = await self.ai.chat(request)

        return self._parse_ai_response(raw_response, vacancies)

    def _format_vacancies(self, vacancies: list[Vacancy]) -> str:
        lines: list[str] = []
        for v in vacancies:
            salary_str = "не указана"
            if v.salary:
                salary_str = (
                    f"{v.salary.from_amount or ''}-{v.salary.to_amount or ''} "
                    f"{v.salary.currency or ''}"
                ).strip()

            lines.append(
                f"ID: {v.id}\n"
                f"Название: {v.name}\n"
                f"Компания: {v.employer.name if v.employer else 'неизвестна'}\n"
                f"Зарплата: {salary_str}\n"
                f"Описание: {v.snippet or 'нет'}\n"
                "---"
            )
        return "\n".join(lines)

    def _parse_ai_response(
        self, raw_response: str, vacancies: list[Vacancy]
    ) -> list[EvaluatedVacancy]:
        try:
            # Очищаем от возможных markdown-тегов ```json ... ```
            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.split("\n", 1)[1]
                clean_json = clean_json.rsplit("```", 1)[0].strip()

            evaluations: list[dict[str, Any]] = json.loads(clean_json)
        except json.JSONDecodeError as err:
            raise VacancyFilterError(f"AI вернул невалидный JSON: {raw_response}") from err

        vacancies_map = {v.id: v for v in vacancies}
        results: list[EvaluatedVacancy] = []

        for item in evaluations:
            v_id = str(item.get("vacancy_id", ""))
            vacancy = vacancies_map.get(v_id)
            if not vacancy:
                continue

            results.append(
                EvaluatedVacancy(
                    vacancy=vacancy,
                    score=int(item.get("score", 0)),
                    match_reasons=item.get("match_reasons", []),
                    gaps=item.get("gaps", []),
                    verdict=str(item.get("verdict", "")),
                )
            )

        # Сортируем по убыванию score
        results.sort(key=lambda x: x.score, reverse=True)
        return results
