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

    if len(crag.crag_name_votes) != 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    crag = Crag(
        **crag.dict(exclude={"crag_name_votes"}),
        crag_name_votes=[
            CragNameVote(
                user_id=user_id,
                **crag_name_vote.dict(),
            )
            for crag_name_vote in crag.crag_name_votes
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
    print(crag_id)
    mongo_crag = mongo.db.crags.find_one({"id": str(crag_id)})
    print(mongo_crag)
    if mongo_crag is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # mongo_crag_name_votes = mongo.db.crag_name_votes.find_one({"crag_id": crag_id})
    # if mongo_crag_name_votes is None:
    #     mongo_crag_name_votes = list()

    return Crag(
        **mongo_crag,
        # crag_name_votes=mongo_crag_name_votes,
    )


@router.post(
    "/crags/{crag_id}/cragNameVotes",
    response_model=CragNameVote,
    status_code=status.HTTP_200_OK,
)
def add_or_update_crag_name_vote(
    crag_id: UUID,
    crag_name_vote: CreateCragNameVote,
):
    mongo_crag_name_vote = mongo.db.crag_name_votes.find_one({"id": crag_id})
    if mongo_crag_name_vote is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    crag_name_vote["vote"]["user_id"] = uuid4()  # TODO
    crag_name_vote = CragNameVote(
        crag_id=crag_id,
        **crag_name_vote,
    )
    mongo.db.crag_name_votes.insert_one(crag_name_vote)
    return crag_name_vote
