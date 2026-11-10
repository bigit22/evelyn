import pytest

from app.ai.prompts import build_cover_letter_user_prompt
from app.services.cover_letter import CoverLetterError, CoverLetterGenerator


def test_build_user_prompt() -> None:
    prompt = build_cover_letter_user_prompt(
        resume="Python dev 3 года",
        vacancy_description="Ищем FastAPI дева",
        company_name="Яндекс",
        company_info="Делаем поиск",
    )
    assert "Python dev 3 года" in prompt
    assert "Ищем FastAPI дева" in prompt
    assert "Яндекс" in prompt
    assert "Делаем поиск" in prompt


def test_parse_ai_response_valid() -> None:
    generator = CoverLetterGenerator(ai_client=None)  # type: ignore[arg-type]
    raw_json = """
    ```json
    {
      "cover_letter": "Здравствуйте! Меня заинтересовал ваш проект...",
      "key_highlights": ["Опыт с FastAPI", "Интерес к поиску"]
    }
    ```
    """
    res = generator._parse_ai_response(raw_json)
    assert "Здравствуйте!" in res.cover_letter
    assert len(res.key_highlights) == 2


def test_parse_ai_response_invalid() -> None:
    generator = CoverLetterGenerator(ai_client=None)  # type: ignore[arg-type]
    with pytest.raises(CoverLetterError, match="невалидный JSON"):
        generator._parse_ai_response("BROKEN JSON")
