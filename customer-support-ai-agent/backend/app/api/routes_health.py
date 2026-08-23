"""GET /health — used by load balancers / container orchestrators."""
from fastapi import APIRouter

from app.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok", "version": "1.0.0"}
