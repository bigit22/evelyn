from pydantic import BaseModel


class ResumeAdaptRequest(BaseModel):
    """Запрос на адаптацию резюме."""

    base_resume: str
    vacancy_description: str
    target_role: str | None = None


class AdaptedResume(BaseModel):
    """Результат адаптации резюме."""

    summary: str
    skills: list[str]
    adapted_experience: str
    key_changes: list[str]
