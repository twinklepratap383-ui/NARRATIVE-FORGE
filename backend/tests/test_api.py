"""API tests via FastAPI's TestClient (offline, mock LLM)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["azure_openai"] in ("mock", "live")


def test_list_scenarios():
    r = client.get("/api/scenarios")
    assert r.status_code == 200
    ids = {s["id"] for s in r.json()}
    assert "victorian_murder" in ids


def test_full_play_flow():
    # Create
    r = client.post("/api/stories", json={"scenario_id": "victorian_murder"})
    assert r.status_code == 200
    story = r.json()
    sid = story["id"]
    assert len(story["scenes"]) == 1  # opening narration

    # Play a dialogue turn
    r = client.post(
        f"/api/stories/{sid}/turn",
        json={"speak_to": "ashworth", "message": "Where were you that night?"},
    )
    assert r.status_code == 200
    turn = r.json()
    assert turn["turn"] == 1
    assert len(turn["scenes"]) == 2

    # Analytics reflects the turn
    r = client.get(f"/api/stories/{sid}/analytics")
    assert r.status_code == 200
    a = r.json()
    assert a["turn"] == 1
    assert "ashworth" in a["emotions"]

    # Accuse the culprit -> solved
    r = client.post(f"/api/stories/{sid}/turn", json={"accuse": "crane"})
    assert r.status_code == 200
    assert r.json()["solved"] is True

    # Further turns are rejected on a solved story
    r = client.post(
        f"/api/stories/{sid}/turn",
        json={"speak_to": "ashworth", "message": "Again?"},
    )
    assert r.status_code == 409


def test_unknown_scenario_404():
    r = client.post("/api/stories", json={"scenario_id": "does_not_exist"})
    assert r.status_code == 404
