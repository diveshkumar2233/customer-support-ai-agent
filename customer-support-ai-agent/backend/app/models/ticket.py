"""Support ticket + tool action audit tables."""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.database.connection import Base


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    reason = Column(Text, nullable=False)
    priority = Column(String, default="normal")  # low|normal|high|urgent
    status = Column(String, default="open")       # open|in_progress|resolved
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ToolAction(Base):
    """Audit log of every tool the agent executed — critical for debugging + trust."""
    __tablename__ = "tool_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    tool_name = Column(String, nullable=False)
    input_payload = Column(JSON, nullable=True)
    output_payload = Column(JSON, nullable=True)
    status = Column(String, default="success")  # success|failed|blocked
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    rating = Column(String, nullable=False)  # thumbs_up|thumbs_down
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # normal|ambiguous|adversarial|edge_case
    faithfulness = Column(String, nullable=True)
    correctness = Column(String, nullable=True)
    retrieval_relevance = Column(String, nullable=True)
    tool_selection_correct = Column(String, nullable=True)
    latency_ms = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
