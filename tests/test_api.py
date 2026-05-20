from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_run_returns_tracking_metadata() -> None:
    response = client.post(
        "/runs",
        json={
            "question": "How should this workflow run?",
            "runtime": "langgraph",
            "provider": "groq",
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["run_id"].startswith("run_")
    assert payload["status"] == "created"
    assert payload["runtime"] == "langgraph"
    assert payload["provider"] == "groq"
