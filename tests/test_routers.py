from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "app": "evelyn"}


def test_vacancies_search_endpoint() -> None:
    resp = client.get("/api/v1/vacancies/search?query=python&per_page=1")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_protected_endpoint_requires_api_key_header() -> None:
    # Запрос без заголовков X-AI-Api-Key должен вернуть 422 (Unprocessable Entity)
    resp = client.post(
        "/api/v1/resume/adapt",
        json={"base_resume": "test", "vacancy_description": "test"},
    )
    assert resp.status_code == 422
