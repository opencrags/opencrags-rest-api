import os
from pathlib import Path
import requests
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


auth = requests.post(
    f"https://{os.environ['AUTH0_DOMAIN']}/oauth/token",
    headers={"content-type": "application/json"},
    data=Path("tests/auth.json").read_text(),
).json()


def test_unauthorized():
    response = client.post("/crags")
    assert response.status_code == 403


def test_add_crag():
    response = client.post(
        "/crags",
        json=dict(),
        headers={"authorization": f"Bearer {auth['access_token']}"},
    )
    assert response.status_code == 201
