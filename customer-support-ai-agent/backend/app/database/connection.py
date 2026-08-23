"""
Database engine + declarative base.

WHY: A single shared SQLAlchemy engine with connection pooling avoids the
cost of opening a new TCP connection to Postgres on every request. Pooling
is essential once you have concurrent users hitting the API.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.settings import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,          # steady-state concurrent connections
    max_overflow=20,       # burst capacity above pool_size
    pool_pre_ping=True,    # detect stale connections before using them
    pool_recycle=1800,     # recycle connections every 30 min
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
