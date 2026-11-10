from typing import Any

import httpx

from app.schemas.vacancy import Employer, Salary, Vacancy

HH_API = "https://api.hh.ru"


class HHParserError(Exception):
    """Ошибка парсера hh.ru."""


class HHParser:
    """Парсер вакансий hh.ru. Работает без авторизации."""

    def __init__(self) -> None:
        self.headers = {
            "User-Agent": "Evelyn/0.1 (evelyn@example.com)",
        }

    async def search(
        self,
        query: str,
        area: int | None = None,
        page: int = 0,
        per_page: int = 20,
    ) -> list[Vacancy]:
        """
        Поиск вакансий.

        Args:
            query: поисковый запрос, например "python backend"
            area: регион (1 = Москва, 2 = СПб, None = все)
            page: номер страницы (с 0)
            per_page: результатов на странице (макс 100)
        """
        params: dict[str, str | int] = {
            "text": query,
            "page": page,
            "per_page": per_page,
        }
        if area is not None:
            params["area"] = area

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{HH_API}/vacancies",
                params=params,
                headers=self.headers,
            )

        if resp.status_code == 429:
            raise HHParserError("Rate limit от hh.ru. Подожди пару секунд.")
        if resp.status_code != 200:
            raise HHParserError(f"hh.ru error {resp.status_code}: {resp.text}")

        data = resp.json()
        return [self._parse_item(item) for item in data.get("items", [])]

    def _parse_item(self, item: dict[str, Any]) -> Vacancy:
        """Превращает сырой JSON из hh.ru в нашу Vacancy."""
        salary_raw = item.get("salary")
        salary = None
        if salary_raw:
            salary = Salary(
                from_amount=salary_raw.get("from"),
                to_amount=salary_raw.get("to"),
                currency=salary_raw.get("currency"),
            )

        employer_raw = item.get("employer")
        employer = None
        if employer_raw:
            employer = Employer(
                name=employer_raw.get("name", ""),
                url=employer_raw.get("alternate_url"),
            )

        snippet_raw = item.get("snippet", {})
        snippet = snippet_raw.get("requirement") or snippet_raw.get("responsibility")

        area_raw = item.get("area", {})

        return Vacancy(
            id=str(item["id"]),
            name=item["name"],
            url=item["alternate_url"],
            salary=salary,
            employer=employer,
            snippet=snippet,
            area=area_raw.get("name"),
        )
