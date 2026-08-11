import httpx
from app.core.config import settings


class AIServiceClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.AI_SERVICE_URL
        self.headers = {"X-Internal-API-Key": settings.INTERNAL_API_KEY}

    async def check_health(self) -> dict:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
            response = await client.get("/health", headers=self.headers)
            response.raise_for_status()
            return response.json()