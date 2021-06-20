import os
from pymongo import MongoClient
from pathlib import Path
import requests
from fastapi.testclient import TestClient
import pytest

from app import main

client = TestClient(main.app)


@pytest.fixture
def auth():
    return requests.post(
        f"https://{os.environ['AUTH0_DOMAIN']}/oauth/token",
        headers={"content-type": "application/json"},
        data=Path("tests/auth.json").read_text(),
    ).json()


def drop_database():
    client = MongoClient(os.environ["DB"])
    client.drop_database("opencrags")


def test_unauthorized():
    response = client.post("/crags")
    assert response.status_code == 403


def test_guest_query():
    response = client.post("/crags/query", json=dict())
    assert response.status_code == 200

    for crag in response.json():
        for vote in crag["name_votes"]:
            assert vote["public"] or vote["user_id"] == ""
    
    return response


def test_crag(auth):
    drop_database()

    response = client.post(
        "/crags",
        json=dict(),
        headers={"authorization": f"Bearer {auth['access_token']}"},
    )
    assert response.status_code == 201
    crag_id = response.json()["id"]

    assert len(test_guest_query().json()) == 1

    response = client.post(
        f"/crags/{crag_id}/name_votes",
        json=dict(
            value="Fagerdala",
            public=False,
        ),
        headers={"authorization": f"Bearer {auth['access_token']}"},
    )
    assert response.status_code == 201
    vote_id = response.json()["id"]

    assert test_guest_query().json()[0]["name_votes"][0]["value"] == "Fagerdala"

    response = client.put(
        f"/crags/{crag_id}/name_votes/{vote_id}",
        json=dict(
            value="Houdini",
            public=True,
        ),
        headers={"authorization": f"Bearer {auth['access_token']}"},
    )
    assert response.status_code == 200

    assert test_guest_query().json()[0]["name_votes"][0]["value"] == "Houdini"

    response = client.delete(
        f"/crags/{crag_id}",
        headers={"authorization": f"Bearer {auth['access_token']}"},
    )
    assert response.status_code == 200
