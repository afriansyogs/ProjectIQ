from fastapi import APIRouter
from app.infrastructure.clients.ai_service_client import AIServiceClient

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    ai_status = "unknown"
    try:
        ai_client = AIServiceClient()
        health_resp = await ai_client.check_health()
        ai_status = health_resp.get("status", "ok")
    except Exception:
        ai_status = "unreachable"

    return {
        "status": "ok",
        "service": "api-service",
        "ai_service_status": ai_status,
    }
