"""
FastAPI dependency that yields a DB session per-request and always closes it.

WHY: Using `yield` inside a dependency guarantees the session is closed
(via the `finally` block) even if the request raises an exception, which
prevents connection leaks under load.
"""
from typing import Generator

from app.database.connection import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
