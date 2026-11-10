import pytest

from app.ai.prompts import build_filter_user_prompt
from app.schemas.vacancy import Vacancy
from app.services.vacancy_filter import VacancyFilter, VacancyFilterError


def test_build_user_prompt() -> None:
    prompt = build_filter_user_prompt("Python Dev", "ID: 1\nTitle: Backend")
    assert "Python Dev" in prompt
    assert "ID: 1" in prompt


def test_parse_ai_response_valid() -> None:
    filter_svc = VacancyFilter(ai_client=None)  # type: ignore[arg-type]
    vacancies = [Vacancy(id="101", name="Python Dev", url="https://hh.ru/101")]
    raw_ai_json = """
    ```json
    [
      {
        "vacancy_id": "101",
        "score": 90,
        "match_reasons": ["Python"],
        "gaps": [],
        "verdict": "Отличный вариант"
      }
    ]
    ```
    """
    res = filter_svc._parse_ai_response(raw_ai_json, vacancies)
    assert len(res) == 1
    assert res[0].score == 90
    assert res[0].vacancy.id == "101"


def test_parse_ai_response_invalid_json() -> None:
    filter_svc = VacancyFilter(ai_client=None)  # type: ignore[arg-type]
    vacancies: list[Vacancy] = []
    with pytest.raises(VacancyFilterError, match="невалидный JSON"):
        filter_svc._parse_ai_response("NOT JSON AT ALL", vacancies)
