from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_page_returns_html() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Evelyn" in response.text
