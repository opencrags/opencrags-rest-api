import os
from pymongo import MongoClient
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import requests
from fastapi.testclient import TestClient
import pytest

from app import main

client = TestClient(main.app)


@pytest.fixture
def auth():
    return requests.post(
        f"""https://{os.environ["AUTH0_DOMAIN"]}/oauth/token""",
        headers={"content-type": "application/json"},
        data=Path("tests/auth.json").read_text(),
    ).json()


def authorized_factory(auth):
    def authorized(fn, *args, **kwargs):
        return fn(
            *args,
            **kwargs,
            headers={"authorization": f"""Bearer {auth["access_token"]}"""}
        )
    return authorized


def drop_database():
    client = MongoClient(os.environ["DB"])
    client.drop_database("opencrags")


def guest_query(user_id):
    response = client.post("/ascents/query", json=dict(user_id=user_id))
    assert response.status_code == 200

    for ascent in response.json():
        assert ascent["public"] or ascent["user_id"] is None
    
    return response


def test_ascents(auth):
    drop_database()

    authorized = authorized_factory(auth)

    user = authorized(client.get, "/users/me").json()

    response = authorized(client.post, "/ascents", json=dict(
        climb_id=str(uuid4()),
        ascent_date=str(datetime.now()),
        public=True,
    ))
    assert response.status_code == 201
    ascent_id = response.json()["id"]

    assert len(guest_query(user["id"]).json()) == 1

    response = authorized(
        client.put,
        f"/ascents/{ascent_id}",
        json=dict(
            ascent_date=str(datetime.now()),
            public=False,
        ),
    )
    assert response.status_code == 200

    response = authorized(client.delete, f"/ascents/{ascent_id}")
    assert response.status_code == 200
