from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.ai.client import AIClient, AIClientError
from app.dependencies import get_ai_client
from app.schemas.vacancy import EvaluatedVacancy, Vacancy
from app.services.hh_parser import HHParser, HHParserError
from app.services.vacancy_filter import VacancyFilter, VacancyFilterError

router = APIRouter(prefix="/api/v1/vacancies", tags=["Vacancies"])


class FilterRequest(BaseModel):
    profile: str
    query: str
    area: int | None = None
    per_page: int = 10


@router.get("/search", response_model=list[Vacancy])
async def search_vacancies(
    query: str = Query(..., description="Поисковый запрос"),
    area: int | None = Query(None, description="ID региона (1=МСК, 2=СПб)"),
    per_page: int = Query(20, ge=1, le=100),
) -> Any:
    """Поиск вакансий на hh.ru без AI."""
    parser = HHParser()
    try:
        return await parser.search(query=query, area=area, per_page=per_page)
    except HHParserError as err:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(err)) from err


@router.post("/search-and-filter", response_model=list[EvaluatedVacancy])
async def search_and_filter_vacancies(
    req: FilterRequest,
    ai_client: Annotated[AIClient, Depends(get_ai_client)],
) -> Any:
    """Поиск вакансий на hh.ru + ранжирование с помощью AI."""
    parser = HHParser()
    try:
        vacancies = await parser.search(query=req.query, area=req.area, per_page=req.per_page)
    except HHParserError as err:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(err)) from err

    v_filter = VacancyFilter(ai_client)
    try:
        return await v_filter.evaluate_vacancies(profile=req.profile, vacancies=vacancies)
    except (AIClientError, VacancyFilterError) as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err
