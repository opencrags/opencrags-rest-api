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


def guest_query(related_id):
    response = client.get(f"/comments?related_id={related_id}")
    assert response.status_code == 200
    
    return response


def test_comments(auth):
    drop_database()

    authorized = authorized_factory(auth)

    related_id = authorized(client.post, "/crags", json=dict()).json()["id"]

    response = authorized(client.post, "/comments", json=dict(
        related_id=related_id,
        related_type="crag",
        comment="first!",
    ))
    assert response.status_code == 201
    comment_id = response.json()["id"]

    assert len(guest_query(related_id).json()) == 1

    response = authorized(client.post, f"/comments/{comment_id}/replies", json=dict(
        comment_id=comment_id,
        reply="seconnd!",
    ))
    assert response.status_code == 201
    reply_id = response.json()["id"]

    response = authorized(
        client.put,
        f"/comments/{comment_id}/replies/{reply_id}",
        json=dict(reply="second!"),
    )
    assert response.status_code == 200
    
    assert guest_query(related_id).json()[0]["replies"][0]["reply"] == "second!"

    response = authorized(client.delete, f"/comments/{comment_id}")
    assert response.status_code == 403

    assert len(guest_query(related_id).json()) == 1
