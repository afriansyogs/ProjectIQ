from typing import Any, Dict, Optional
import httpx
from app.core.config import settings


class AIServiceClient:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url or settings.AI_SERVICE_URL
        self.headers = {"X-Internal-API-Key": settings.INTERNAL_API_KEY}

    async def check_health(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
            response = await client.get("/health", headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def ingest_document(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            response = await client.post("/documents/ingest", json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def query_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            response = await client.post("/chat/query", json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()