from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DocumentIngestRequest(BaseModel):
    document_id: str = Field(
        ...,
        description="id document"
    )
    title: str = Field(
        ...,
        description="File name"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="text"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadata - author, kategori, or tag"
    )

class DocumentIngestResponse(BaseModel):
    status: str = "success"
    document_id: str
    total_chunks: int = Field(
        ...,
        description="Chunks that have been successfully created and vectorized"
    )
    message: str

class SourceNode(BaseModel):
    document_id: str
    title: str
    chunk_index: int
    text: str = Field(..., description="text chunk")
    score: float = Field(..., ge=0.0, le=1.0, description="similarity score 0-1")

class ChatQueryRequest(BaseModel):
    question: str = Field(
        ..., 
        min_length=2, 
        description="question user"
    )
    top_k: int = Field(
        default=4, 
        ge=1, 
        le=10, 
        description="Amount of chunk retrieve"
    )

class ChatQueryResponse(BaseModel):
    answer: str = Field(..., description="Answer from LLM ")
    sources: List[SourceNode] = Field(
        default_factory=list, 
        description="Source node"
    )
    model_used: str = Field(..., description="Model LLM")