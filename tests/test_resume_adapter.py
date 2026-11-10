import pytest

from app.ai.prompts import build_resume_adapt_user_prompt
from app.services.resume_adapter import ResumeAdapter, ResumeAdapterError


def test_build_user_prompt() -> None:
    prompt = build_resume_adapt_user_prompt("Мое резюме", "Описание вакансии", "Senior Dev")
    assert "Мое резюме" in prompt
    assert "Описание вакансии" in prompt
    assert "Senior Dev" in prompt


def test_parse_ai_response_valid() -> None:
    adapter = ResumeAdapter(ai_client=None)  # type: ignore[arg-type]
    raw_json = """
    ```json
    {
      "summary": "Разработчик с опытом Python",
      "skills": ["Python", "FastAPI"],
      "adapted_experience": "Работал над микросервисами",
      "key_changes": ["Добавлены акценты на FastAPI"]
    }
    ```
    """
    res = adapter._parse_ai_response(raw_json)
    assert res.summary == "Разработчик с опытом Python"
    assert "FastAPI" in res.skills
    assert len(res.key_changes) == 1


def test_parse_ai_response_invalid() -> None:
    adapter = ResumeAdapter(ai_client=None)  # type: ignore[arg-type]
    with pytest.raises(ResumeAdapterError, match="невалидный JSON"):
        adapter._parse_ai_response("BROKEN JSON")
