from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_missing_checkpoint_is_honest() -> None:
    response = client.post(
        "/api/predict?model=improved",
        files={"file": ("not-image.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415

