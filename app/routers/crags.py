from fastapi import APIRouter, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
import random
import io
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Union, Literal, Optional

from app.items.crag import (
    MongoCrag,
    MongoCragNameVote,
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
async def list_crags():
    mongo_crags = await mongo.engine.find(MongoCrag)

    return [
        Crag(
            **mongo_crag.dict(),
            crag_name_votes=list(),  # TODO
        )
        for mongo_crag in mongo_crags
    ]


@router.post(
    "/crags",
    response_model=Crag,
    status_code=status.HTTP_201_CREATED,
)
async def add_crag(crag: CreateCrag):
    mongo_crag = MongoCrag(
        user_id=mongo.ObjectId(), # TODO: use real user
    )
    await mongo.engine.save(mongo_crag)
    return Crag(
        **mongo_crag.dict(),
        crag_name_votes=list(),
    )


@router.delete(
    "/crags/{crag_id}",
    status_code=status.HTTP_200_OK,
)
async def remove_crag(
    crag_id: mongo.ObjectId,
):
    mongo_crag = await mongo.engine.find_one(MongoCrag, MongoCrag.id == crag_id)
    if mongo_crag is None:
        raise HTTPException(404)
    await mongo.engine.delete(mongo_crag)
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/crags/{crag_id}",
    response_model=Crag,
    status_code=status.HTTP_200_OK,
)
async def view_crag(
    crag_id: mongo.ObjectId,
):
    mongo_crag = await mongo.engine.find_one(MongoCrag, MongoCrag.id == crag_id)
    if mongo_crag is None:
        raise HTTPException(404)
    return Crag(
        **mongo_crag.dict(),
        crag_name_votes=list(),  # TODO
    )


@router.post(
    "/crags/{crag_id}/cragNameVotes",
    response_model=CragNameVote,
    status_code=status.HTTP_200_OK,
)
async def add_or_update_crag_name_vote(
    crag_id: mongo.ObjectId,
    crag_name_vote: CreateCragNameVote,
):
    crag = await mongo.engine.find_one(MongoCrag, MongoCrag.id == crag_id)
    if crag is None:
        raise HTTPException(404)

    crag_name_vote = crag_name_vote.dict()
    crag_name_vote["vote"]["user_id"] = mongo.ObjectId()  # TODO
    crag_name_vote = MongoCragNameVote(
        crag_id=crag_id,
        **crag_name_vote,
    )
    await mongo.engine.save(crag_name_vote)
    return crag_name_vote
