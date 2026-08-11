from fastapi import FastAPI, Header, HTTPException, status, Depends
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)


async def verify_internal_api_key(x_internal_api_key: str = Header(...)):
    if x_internal_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid or missing internal API key.",
        )


@app.get("/health", dependencies=[Depends(verify_internal_api_key)])
async def health_check():
    return {"status": "ok", "service": "ai-service"}
