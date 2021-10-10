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


def guest_query(user_id):
    response = client.post("/crags/query", json=dict(user_id=user_id))
    assert response.status_code == 200

    for crag in response.json():
        for vote in crag["name_votes"]:
            assert vote["public"] or vote["user_id"] is None
    
    return response


def test_crag(auth):
    drop_database()

    authorized = authorized_factory(auth)

    user = authorized(client.get, "/users/me").json()

    response = authorized(client.post, "/crags", json=dict())
    assert response.status_code == 201
    crag_id = response.json()["id"]

    assert len(guest_query(user["id"]).json()) == 1

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

    assert guest_query(user["id"]).json()[0]["name_votes"][0]["value"] == "Fagerdala"

    response = authorized(
        client.put,
        f"/crags/{crag_id}/name_votes/{vote_id}",
        json=dict(
            value="Houdini",
            public=True,
        ),
    )
    assert response.status_code == 200

    assert guest_query(user["id"]).json()[0]["name_votes"][0]["value"] == "Houdini"

    response = authorized(client.post, "/sectors", json=dict(crag_id=crag_id))
    assert response.status_code == 201
    sector_id = response.json()["id"]

    assert len(guest_query(user["id"]).json()) == 1

    response = authorized(
        client.post,
        f"/sectors/{sector_id}/name_votes",
        json=dict(
            value="Gräddhyllan",
            public=True,
        ),
    )
    assert response.status_code == 201

    response = authorized(
        client.get,
        f"/quick-search?text=grädd",
    )
    assert response.status_code == 200
    assert response.json()[0]["sector"]["name_votes"][0]["value"] == "Gräddhyllan"

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

    response = authorized(client.post, "/crags", json=dict())
    assert response.status_code == 201
    crag_id2 = response.json()["id"]

    response = authorized(client.put, f"/sectors/{sector_id}", json=dict(crag_id=crag_id2))
    assert response.status_code == 200
