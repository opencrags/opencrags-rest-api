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

from app.items.ascent import Ascent, AscentId, IdentifiedAscent


router = APIRouter(
    tags=["ascents"],
)


@router.post(
    "/ascents",
    response_model=AscentId,
    status_code=status.HTTP_201_CREATED,
)
def add_ascent(
    ascent: Ascent,
):
    return AscentId(id=UUID(int=random.getrandbits(128)))



@router.put(
    "/ascents/{ascent_id}",
    response_model=IdentifiedAscent,
    status_code=status.HTTP_200_OK,
)
def update_ascent(
    ascent_id: UUID,
    ascent: Ascent,
):
    pass


@router.delete(
    "/ascents/{ascent_id}",
    status_code=status.HTTP_200_OK,
)
def remove_ascent(
    ascent_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/ascents/{ascent_id}",
    response_model=IdentifiedAscent,
    status_code=status.HTTP_200_OK,
)
def view_ascent(
    ascent_id: UUID,
):
    pass


@router.get(
    "/ascents",
    response_model=List[IdentifiedAscent],
    status_code=status.HTTP_200_OK,
)
def list_ascents(
    climd_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
):
    pass


@router.get(
    "/ascents/summary",
    # response_model=List[IdentifiedAscent],
    status_code=status.HTTP_200_OK,
)
def summary_of_private_and_public_ascents(
    climd_id: Optional[UUID] = None,
):
    pass
