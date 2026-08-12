from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_rate_limit():
    responses = []

    for _ in range(6):
        response = client.get("/api/data")
        responses.append(response.status_code)

    assert 200 in responses
    assert 429 in responses