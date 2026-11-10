from typing import Annotated

from fastapi import Header, HTTPException, status

from app.ai.client import AIClient, InvalidAPIKeyError


def get_ai_client(
    x_ai_api_key: Annotated[str, Header(description="API key for AI provider")],
    x_ai_provider: Annotated[
        str, Header(description="AI Provider (openrouter | gemini)")
    ] = "openrouter",
) -> AIClient:
    """Инжектит AIClient с ключом и провайдером из заголовков запроса."""
    try:
        return AIClient(provider=x_ai_provider, api_key=x_ai_api_key)
    except (ValueError, InvalidAPIKeyError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
        ) from err
