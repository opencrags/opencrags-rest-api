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

    related_id = str(uuid4())

    response = authorized(client.post, "/comments", json=dict(
        related_ids=[related_id],
        comment="first!",
    ))
    assert response.status_code == 201
    comment_id = response.json()["id"]

    assert len(guest_query(related_id).json()) == 1

    response = authorized(client.post, "/comments", json=dict(
        related_ids=[related_id],
        comment="first!",
    ))
    assert response.status_code == 201
    second_comment_id = response.json()["id"]

    assert len(guest_query(related_id).json()) == 2

    response = authorized(
        client.put,
        f"/comments/{second_comment_id}",
        json=dict(
            comment="second!"
        ),
    )
    assert response.status_code == 200

    response = authorized(client.delete, f"/comments/{comment_id}")
    assert response.status_code == 200

    assert len(guest_query(related_id).json()) == 1
