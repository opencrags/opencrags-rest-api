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


def authorized_factory(auth):
    def authorized(fn, *args, **kwargs):
        return fn(
            *args,
            **kwargs,
            headers={"authorization": f"Bearer {auth['access_token']}"}
        )
    return authorized


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
            assert vote["public"] or vote["user_id"] == None
    
    return response


def test_crag(auth):
    drop_database()

    authorized = authorized_factory(auth)

    response = authorized(client.post, "/crags", json=dict(grade_system="Hueco scale"))
    assert response.status_code == 201
    crag_id = response.json()["id"]

    assert len(test_guest_query().json()) == 1

    response = authorized(
        client.post,
        f"/crags/{crag_id}/name_votes",
        json=dict(
            value="Fagerdala",
            public=False,
        ),
    )
    assert response.status_code == 201
    vote_id = response.json()["id"]

    assert test_guest_query().json()[0]["name_votes"][0]["value"] == "Fagerdala"

    response = authorized(
        client.put,
        f"/crags/{crag_id}/name_votes/{vote_id}",
        json=dict(
            value="Houdini",
            public=True,
        ),
    )
    assert response.status_code == 200

    assert test_guest_query().json()[0]["name_votes"][0]["value"] == "Houdini"

    response = authorized(client.post, f"/sectors", json=dict(crag_id=crag_id))
    assert response.status_code == 201
    sector_id = response.json()["id"]

    response = authorized(
        client.post,
        f"/sectors/{sector_id}/name_votes",
        json=dict(
            value="Houdini",
            public=True,
        ),
    )

    response = authorized(
        client.post,
        f"/sectors/{sector_id}/coordinate_votes",
        json=dict(
            value=[17.645371, 59.855488],
            public=False,
        ),
    )
    response = authorized(client.delete, f"/crags/{crag_id}")
    assert response.status_code == 200
