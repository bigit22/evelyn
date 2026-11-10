from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.client import AIClient, AIClientError
from app.dependencies import get_ai_client
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse
from app.services.cover_letter import CoverLetterError, CoverLetterGenerator

router = APIRouter(prefix="/api/v1/cover-letter", tags=["Cover Letter"])


@router.post("/generate", response_model=CoverLetterResponse)
async def generate_cover_letter(
    req: CoverLetterRequest,
    ai_client: Annotated[AIClient, Depends(get_ai_client)],
) -> Any:
    """Генерация персонализированного сопроводительного письма."""
    generator = CoverLetterGenerator(ai_client)
    try:
        return await generator.generate(req)
    except (AIClientError, CoverLetterError) as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err
