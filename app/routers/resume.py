from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.client import AIClient, AIClientError
from app.dependencies import get_ai_client
from app.schemas.resume import AdaptedResume, ResumeAdaptRequest
from app.services.resume_adapter import ResumeAdapter, ResumeAdapterError

router = APIRouter(prefix="/api/v1/resume", tags=["Resume"])


@router.post("/adapt", response_model=AdaptedResume)
async def adapt_resume(
    req: ResumeAdaptRequest,
    ai_client: Annotated[AIClient, Depends(get_ai_client)],
) -> Any:
    """Адаптация резюме под вакансию с помощью AI."""
    adapter = ResumeAdapter(ai_client)
    try:
        return await adapter.adapt(req)
    except (AIClientError, ResumeAdapterError) as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err
