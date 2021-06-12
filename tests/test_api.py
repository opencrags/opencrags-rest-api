from uuid import UUID
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_unauthorized():
    response = client.post("/crags")
    assert response.status_code == 403
