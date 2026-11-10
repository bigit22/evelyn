from typing import Any

from app.schemas.vacancy import Vacancy
from app.services.hh_parser import HHParser


class TestParseItem:
    """Тесты парсинга одного элемента (без сети)."""

    def setup_method(self) -> None:
        self.parser = HHParser()

    def test_full_item(self) -> None:
        raw = {
            "id": "12345",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/12345",
            "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
            "employer": {"name": "Яндекс", "alternate_url": "https://hh.ru/employer/123"},
            "snippet": {"requirement": "Python 3.11+, FastAPI"},
            "area": {"name": "Москва"},
        }
        v = self.parser._parse_item(raw)
        assert v.id == "12345"
        assert v.name == "Python Developer"
        assert v.salary is not None
        assert v.salary.from_amount == 150000
        assert v.employer is not None
        assert v.employer.name == "Яндекс"
        assert v.area == "Москва"

    def test_minimal_item(self) -> None:
        raw: dict[str, Any] = {
            "id": "99",
            "name": "Junior Dev",
            "alternate_url": "https://hh.ru/vacancy/99",
            "salary": None,
            "employer": None,
            "snippet": {},
            "area": {},
        }
        v = self.parser._parse_item(raw)
        assert v.salary is None
        assert v.employer is None
        assert v.snippet is None

    def test_returns_vacancy_type(self) -> None:
        raw = {
            "id": "1",
            "name": "Test",
            "alternate_url": "https://hh.ru/vacancy/1",
        }
        v = self.parser._parse_item(raw)
        assert isinstance(v, Vacancy)
