from pydantic import BaseModel


class CoverLetterRequest(BaseModel):
    """Запрос на генерацию сопроводительного письма."""

    resume: str
    vacancy_description: str
    company_name: str
    company_info: str | None = None  # Инфа о компании (продукты, новости и т.д.)


class CoverLetterResponse(BaseModel):
    """Результат генерации сопроводительного письма."""

    cover_letter: str
    key_highlights: list[str]  # На чём сделан акцент в письме
