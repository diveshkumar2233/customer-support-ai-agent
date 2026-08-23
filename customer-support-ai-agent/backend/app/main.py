"""
FastAPI application entrypoint.

WHY the middleware order matters: request-id assignment happens first so
every downstream log line (including error handlers) can be correlated;
CORS is applied before routing so preflight requests are handled correctly.
"""
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    routes_chat,
    routes_documents,
    routes_health,
    routes_orders,
    routes_refunds,
    routes_tickets,
)
from app.config.settings import get_settings
from app.database.connection import Base, engine

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-oriented Agentic AI + RAG customer support backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-ms"] = f"{duration_ms:.2f}"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak stack traces / internals to the client.
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(routes_health.router, prefix=settings.API_PREFIX)
app.include_router(routes_chat.router, prefix=settings.API_PREFIX)
app.include_router(routes_documents.router, prefix=settings.API_PREFIX)
app.include_router(routes_orders.router, prefix=settings.API_PREFIX)
app.include_router(routes_tickets.router, prefix=settings.API_PREFIX)
app.include_router(routes_refunds.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def on_startup():
    # For a portfolio/demo project we auto-create tables; production systems
    # should use Alembic migrations instead (see database/migrations/).
    Base.metadata.create_all(bind=engine)
