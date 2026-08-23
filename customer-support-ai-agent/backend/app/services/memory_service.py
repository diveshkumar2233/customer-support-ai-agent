"""
Short-term conversation memory.

WHY windowed memory, not the full history: sending the entire conversation
history to the LLM on every turn grows cost/latency linearly and eventually
exceeds the context window. We keep the last N turns (settings.
MAX_CONVERSATION_TURNS_IN_MEMORY) in the prompt and rely on the database
for full long-term history (e.g. for human agents reviewing a handoff).
We deliberately do NOT store full tool payloads (e.g. raw customer PII) in
the in-memory window — only role/content — to limit what gets replayed
into future prompts.
"""
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.models.message import Message

settings = get_settings()


def get_recent_history(db: Session, conversation_id: str) -> list[dict]:
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(settings.MAX_CONVERSATION_TURNS_IN_MEMORY)
        .all()
    )
    messages.reverse()
    return [{"role": m.role, "content": m.content} for m in messages]


def save_message(db: Session, conversation_id: str, role: str, content: str, **kwargs) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content, **kwargs)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
