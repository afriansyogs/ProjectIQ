from fastapi import FastAPI, Header, HTTPException, status, Depends
from app.core.config import settings
from app.schemas.rag import(
    DocumentIngestRequest,
    DocumentIngestResponse,
    ChatQueryRequest,
    ChatQueryResponse,
)
from app.services.rag_service import rag_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


async def verify_internal_api_key(x_internal_api_key: str = Header(...)):
    if x_internal_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid or missing internal API key.",
        )


@app.get("/health", dependencies=[Depends(verify_internal_api_key)])
async def health_check():
    return {"status": "ok", "service": "ai-service"}

@app.post(
    "/documents/ingest",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["RAG Ingestion"],
    dependencies=[Depends(verify_internal_api_key)],
    summary="Ingest and Index Document into Qdrant",
)
async def ingest_document_endpoint(data: DocumentIngestRequest):                                                                                                                                                                                                                                                                                                                      
    try:
        response = await rag_service.ingest_document(data)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed process document: {str(e)}",
        )

@app.post(
    "/chat/query",
    response_model=ChatQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["RAG Chat"],
    dependencies=[Depends(verify_internal_api_key)],
    summary="Ask Question to Knowladge Base",
)
async def chat_query_endpoint(req: ChatQueryRequest):
    try:
        response = await rag_service.query_chat(req)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed answer question: {str(e)}",
        )