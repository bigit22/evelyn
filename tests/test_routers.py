from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.vacancy import Vacancy

client = TestClient(app)


def test_healthcheck() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "app": "evelyn"}


@patch("app.services.hh_parser.HHParser.search", new_callable=AsyncMock)
def test_vacancies_search_endpoint(mock_search: AsyncMock) -> None:
    # Заменяем реальный запрос на hh.ru поддельным ответом
    mock_search.return_value = [Vacancy(id="123", name="Python Developer", url="https://hh.ru/123")]

    resp = client.get("/api/v1/vacancies/search?query=python&per_page=1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "123"
    mock_search.assert_awaited_once()


def test_protected_endpoint_requires_api_key_header() -> None:
    resp = client.post(
        "/api/v1/resume/adapt",
        json={"base_resume": "test", "vacancy_description": "test"},
    )
    assert resp.status_code == 422
