"""Smoke: healthz -> start -> respond -> chain -> graph (single local user, no auth)."""

from fastapi.testclient import TestClient

from app.main import app


def test_api_smoke():
    c = TestClient(app)

    r = c.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    r = c.post(
        "/api/session/start",
        json={"topic": "Free will", "context": "smoke"},
    )
    assert r.status_code == 200
    sid = r.json()["session_id"]

    r = c.post(
        "/api/session/respond",
        json={"session_id": sid, "message": "You are an idiot, so you are wrong"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ai_question"].endswith("?")

    r = c.get(f"/api/session/{sid}/chain")
    assert r.status_code == 200

    r = c.get(f"/api/session/{sid}/graph")
    assert r.status_code == 200
    assert len(r.json()["nodes"]) > 0
