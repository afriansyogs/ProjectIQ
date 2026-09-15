import secrets
from fastapi import Header, HTTPException, status
from app.core.config import settings


async def verify_internal_api_key(x_internal_api_key: str = Header(...)) -> str:
    if not secrets.compare_digest(x_internal_api_key, settings.INTERNAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid or missing internal API key.",
        )
    return x_internal_api_key
