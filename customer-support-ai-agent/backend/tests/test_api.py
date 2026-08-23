"""API-level smoke tests using FastAPI's TestClient (health + orders endpoints,
which don't require a live LLM call)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
