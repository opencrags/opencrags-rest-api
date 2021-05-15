from fastapi import APIRouter, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
import random
import io
from uuid import UUID
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Union, Literal, Optional

from app.items.crag import Crag, CragId, IdentifiedCrag


router = APIRouter(
    tags=["crags"],
)


@router.post(
    "/crags",
    response_model=CragId,
    status_code=status.HTTP_201_CREATED,
)
def add_crag(crag: Crag):
    crag_id = UUID(int=random.getrandbits(128))
    return CragId(id=crag_id)


@router.put(
    "/crags/{crag_id}",
    response_model=Crag,
    status_code=status.HTTP_200_OK,
)
def update_crag(crag_id: UUID, crag: Crag):
    crag_id = UUID(int=random.getrandbits(128))
    return CragId(id=crag_id)


@router.delete(
    "/crags/{crag_id}",
    status_code=status.HTTP_200_OK,
)
def remove_crag(
    crag_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/crags/{crag_id}",
    response_model=IdentifiedCrag,
    status_code=status.HTTP_200_OK,
)
def view_crag():
    pass

