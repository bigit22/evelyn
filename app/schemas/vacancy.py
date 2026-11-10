from pydantic import BaseModel


class Salary(BaseModel):
    from_amount: int | None = None
    to_amount: int | None = None
    currency: str | None = None


class Employer(BaseModel):
    name: str
    url: str | None = None


class Vacancy(BaseModel):
    """Вакансия с hh.ru."""

    id: str
    name: str
    url: str
    salary: Salary | None = None
    employer: Employer | None = None
    snippet: str | None = None
    area: str | None = None


class SearchResponse(BaseModel):
    """Результат поиска."""

    query: str
    found: int
    vacancies: list[Vacancy]


class EvaluatedVacancy(BaseModel):
    """Вакансия с оценкой от AI."""

    vacancy: Vacancy
    score: int  # 0..100
    match_reasons: list[str]
    gaps: list[str]
    verdict: str
