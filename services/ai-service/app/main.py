from fastapi import Depends, FastAPI, HTTPException, status
from app.core.config import settings
from app.core.security import verify_internal_api_key
from app.schemas.rag import (
    ChatQueryRequest,
    ChatQueryResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
)
from app.services.rag_service import rag_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health", tags=["Health"], dependencies=[Depends(verify_internal_api_key)])
async def health_check() -> dict:
    return {"status": "ok", "service": "ai-service"}


@app.post(
    "/documents/ingest",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["RAG Ingestion"],
    dependencies=[Depends(verify_internal_api_key)],
    summary="Ingest and Index Document into Qdrant",
)
async def ingest_document_endpoint(data: DocumentIngestRequest) -> DocumentIngestResponse:
    try:
        response = await rag_service.ingest_document(data)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}",
        )


@app.post(
    "/chat/query",
    response_model=ChatQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["RAG Chat"],
    dependencies=[Depends(verify_internal_api_key)],
    summary="Ask Question to Knowledge Base",
)
async def chat_query_endpoint(req: ChatQueryRequest) -> ChatQueryResponse:
    try:
        response = await rag_service.query_chat(req)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat query: {str(e)}",
        )