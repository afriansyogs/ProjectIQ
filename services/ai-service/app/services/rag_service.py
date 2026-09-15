import uuid
from typing import List
from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient, models
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.schemas.rag import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    ChatQueryRequest,
    ChatQueryResponse,
    SourceNode,
)


class RAGService:
    def __init__(self) -> None:
        self.ai_client = AsyncOpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url=settings.GEMINI_BASE_URL,
        )
        self.qdrant_client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    async def ingest_document(self, data: DocumentIngestRequest) -> DocumentIngestResponse:
        chunks: List[str] = self.text_splitter.split_text(data.content)
        if not chunks:
            chunks = [data.content]

        # batch embeddings
        embed_response = await self.ai_client.embeddings.create(
            input=chunks,
            model=settings.EMBEDDING_MODEL,
            dimensions=768,
        )

        points = []
        for i, (chunk_text, emb_item) in enumerate(zip(chunks, embed_response.data)):
            # Deterministic UUID
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{data.document_id}:{i}"))

            payload = {
                "document_id": data.document_id,
                "title": data.title,
                "chunk_index": i,
                "text": chunk_text,
                "char_length": len(chunk_text),
                **(data.metadata or {}),
            }

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=emb_item.embedding,
                    payload=payload,
                )
            )

        await self.qdrant_client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points,
        )

        return DocumentIngestResponse(
            document_id=data.document_id,
            total_chunks=len(points),
            message=f"Successfully indexed {len(points)} chunks into collection '{settings.QDRANT_COLLECTION_NAME}'.",
        )

    async def query_chat(self, req: ChatQueryRequest) -> ChatQueryResponse:
        query_embed_resp = await self.ai_client.embeddings.create(
            input=[req.question],
            model=settings.EMBEDDING_MODEL,
            dimensions=768,
        )
        query_vector = query_embed_resp.data[0].embedding

        search_results = await self.qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=req.top_k,
            with_payload=True,
        )

        sources: List[SourceNode] = []
        for hit in search_results.points:
            p = hit.payload or {}
            sources.append(
                SourceNode(
                    document_id=p.get("document_id", ""),
                    title=p.get("title", "Unknown"),
                    chunk_index=p.get("chunk_index", 0),
                    text=p.get("text", ""),
                    score=round(float(hit.score), 4),
                )
            )

        if not sources:
            return ChatQueryResponse(
                answer="No relevant information was found in the indexed documents to answer your question.",
                sources=[],
                model_used=settings.CHAT_MODEL,
            )

        context_blocks = [
            f"Document: {s.title} (ID: {s.document_id}), Chunk {s.chunk_index}\n"
            f"Score: {s.score}\n"
            f"Content:\n{s.text}"
            for s in sources
        ]
        context_text = "\n\n".join(context_blocks)

        system_prompt = (
            "You are an expert AI assistant for the enterprise ProjectIQ Knowledge Base.\n"
            "Your task: Answer user questions strictly and exclusively using the provided document excerpts.\n"
            "Strict Guidelines:\n"
            "1. Ground all claims directly in the provided context.\n"
            "2. If the context does not contain sufficient facts to answer, explicitly and politely state that the information is not present in the documents.\n"
            "3. Do not invent, extrapolate, or assume facts beyond what is written.\n"
            "4. Cite the source document title when referencing facts."
        )

        user_prompt = (
            f"Document context:\n"
            f"-----------------\n"
            f"{context_text}\n"
            f"-----------------\n\n"
            f"User question: {req.question}"
        )

        completion = await self.ai_client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        answer_text = completion.choices[0].message.content or ""

        return ChatQueryResponse(
            answer=answer_text,
            sources=sources,
            model_used=settings.CHAT_MODEL,
        )


rag_service = RAGService()