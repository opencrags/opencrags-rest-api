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

from app.items.crag import Crag, CragNameVote
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
    crags = await mongo.engine.find(Crag)
    return crags


@router.put(
    "/crags",
    response_model=Crag,
    status_code=status.HTTP_200_OK,
)
async def add_crag(crag: Crag):
    crag_ = await mongo.engine.find_one(Crag, Crag.id == crag.id)
    if crag_ is not None:
        raise HTTPException(409)
    await mongo.engine.save(crag)
    return crag


@router.delete(
    "/crags/{crag_id}",
    status_code=status.HTTP_200_OK,
)
async def remove_crag(
    crag_id: mongo.ObjectId,
):
    crag = await mongo.engine.find_one(Crag, Crag.id == crag_id)
    if crag is None:
        raise HTTPException(404)
    await mongo.engine.delete(crag)
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/crags/{crag_id}",
    response_model=Crag,
    status_code=status.HTTP_200_OK,
)
async def view_crag(
    crag_id: mongo.ObjectId,
):
    crag = await mongo.engine.find_one(Crag, Crag.id == crag_id)
    if crag is None:
        raise HTTPException(404)
    return crag


@router.put(
    "/crags/{crag_id}/cragNameVotes",
    response_model=CragNameVote,
    status_code=status.HTTP_200_OK,
)
async def add_or_update_crag_name_vote(
    crag_id: mongo.ObjectId,
    crag_name_vote: CragNameVote,
):
    assert crag_id == crag_name_vote.crag_id or crag_name_vote.crag_id is None
    crag_name_vote.crag_id = crag_id
    crag = await mongo.engine.find_one(Crag, Crag.id == crag_name_vote.crag_id)
    if crag is None:
        raise HTTPException(404)

    await mongo.engine.save(crag_name_vote)
    return crag_name_vote
