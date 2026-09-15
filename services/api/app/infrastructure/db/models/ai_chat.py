import enum
import uuid
from typing import Optional
from sqlalchemy import Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base


class SessionType(str, enum.Enum):
    RAG_KNOWLEDGE = "RAG_KNOWLEDGE"
    EXECUTIVE_AUDIT = "EXECUTIVE_AUDIT"


class SenderType(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class AIChatSession(Base):
    __tablename__ = "ai_chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    session_type: Mapped[SessionType] = mapped_column(
        SQLEnum(SessionType, name="session_type"),
        default=SessionType.RAG_KNOWLEDGE,
        nullable=False,
    )


class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_type: Mapped[SenderType] = mapped_column(
        SQLEnum(SenderType, name="sender_type"),
        nullable=False,
    )
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    sources_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
