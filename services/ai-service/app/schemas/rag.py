from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# INGESTION SCHEMAS
class DocumentIngestRequest(BaseModel):
    document_id: str = Field(
        ...,
        description="Unique identifier of the document (UUID) matching the relational database",
    )
    title: str = Field(
        ...,
        description="Original document title or filename, e.g., 'Payment_Gateway_PRD.pdf'",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Raw textual content extracted from the document to be chunked and indexed",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional metadata key-values such as author, category, or access tags",
    )

class DocumentIngestResponse(BaseModel):
    status: str = Field(default="success", description="Status string indicator")
    document_id: str = Field(..., description="ID of the processed document")
    total_chunks: int = Field(
        ...,
        description="Total number of text chunks created, embedded, and stored",
    )
    message: str = Field(..., description="Human-readable status summary message")


# QUERY/RAG SCHEMAS (Retrieval and Synthesis)
class SourceNode(BaseModel):
    document_id: str = Field(..., description="ID of the document this excerpt originates from")
    title: str = Field(..., description="Title of the source document")
    chunk_index: int = Field(..., description="Sequential position index of the chunk")
    text: str = Field(..., description="Verbatim text excerpt retrieved from the chunk")
    score: float = Field(
        ...,
        description="Cosine similarity relevance score between query and chunk",
    )

class ChatQueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        description="User question to be answered against indexed documents",
    )
    top_k: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Maximum number of relevant document chunks to retrieve",
    )

class ChatQueryResponse(BaseModel):
    answer: str = Field(..., description="Synthesized natural language answer from the LLM")
    sources: List[SourceNode] = Field(
        default_factory=list,
        description="List of citation nodes used as grounded context for the answer",
    )
    model_used: str = Field(..., description="Name of the LLM model that generated the answer")