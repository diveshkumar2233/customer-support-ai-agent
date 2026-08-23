"""Message table: every user/assistant/tool turn in a conversation."""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user | assistant | tool | system
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)          # RAG citations
    tool_calls = Column(JSON, nullable=True)        # tools invoked for this turn
    confidence = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    token_usage = Column(JSON, nullable=True)       # {"input": int, "output": int}
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
