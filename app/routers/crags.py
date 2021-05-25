from fastapi import APIRouter, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
from uuid import UUID, uuid4
import io
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Union, Literal, Optional

from app.items.crag import (
    CreateCrag,
    Crag,
    CreateCragNameVote,
    CragNameVote,
    Vote,
)
from app import mongo


router = APIRouter(
    tags=["crags"],
)

# POST /crags
# POST /crags/{crag_id}/votes
# POST /crags/{crag_id}/votes


# this wont work when there are multiple thing to vote about?
# POST /climbs/{climb_id}/gradeVotes
# POST /climbs/{climb_id}/ratings


@router.get(
    "/crags",
    response_model=List[Crag],
    status_code=status.HTTP_200_OK,
)
def list_crags():
    mongo_crags = mongo.db.crags.find()

    return [
        Crag(**mongo_crag)
        for mongo_crag in mongo_crags
    ]


@router.post(
    "/crags",
    response_model=Crag,
    status_code=status.HTTP_201_CREATED,
)
def add_crag(crag: CreateCrag):
    user_id = uuid4() #  TODO: use real user

    if len(crag.name_votes) != 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    crag = Crag(
        **crag.dict(exclude={"name_votes"}),
        name_votes=[
            CragNameVote(
                user_id=user_id,
                **name_vote.dict(),
            )
            for name_vote in crag.name_votes
        ],
        user_id=user_id,
    )
    mongo.db.crags.insert_one(crag.dict())
    return crag


@router.delete(
    "/crags/{crag_id}",
    status_code=status.HTTP_200_OK,
)
def remove_crag(
    crag_id: UUID,
):
    mongo_crag = mongo.db.crags.find_one({"id": crag_id})
    if mongo_crag is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    mongo.db.crags.delete_one({"id": crag_id})
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/crags/{crag_id}",
    response_model=Crag,
    status_code=status.HTTP_200_OK,
)
def view_crag(
    crag_id: UUID,
):
    mongo_crag = mongo.db.crags.find_one({"id": crag_id})
    if mongo_crag is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return Crag(**mongo_crag)


@router.post(
    "/crags/{crag_id}/name-votes",
    response_model=CragNameVote,
    status_code=status.HTTP_200_OK,
)
def add_name_vote(
    crag_id: UUID,
    name_vote: CreateCragNameVote,
):
    name_vote = CragNameVote(
        user_id=uuid4(), #  TODO: replace with real user id
        **name_vote.dict(),
    )
    mongo_crag = mongo.db.crags.find_one({"id": crag_id})
    crag = Crag(**mongo_crag)
    crag.name_votes.append(name_vote)
    mongo.db.crags.replace_one({"id": crag_id}, crag.dict())
    return name_vote
