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

from app.items.line import Line, LineId, IdentifiedLine


router = APIRouter(
    tags=["lines"],
)


@router.post(
    "/lines",
    response_model=LineId,
    status_code=status.HTTP_201_CREATED,
)
def add_line(
    climb_id: UUID,
    line: Line,
):
    return LineId(id=UUID(int=random.getrandbits(128)))


@router.put(
    "/lines/{line_id}",
    response_model=IdentifiedLine,
    status_code=status.HTTP_200_OK,
)
def update_line(
    line_id: UUID,
    line: Line,
):
    pass


@router.delete(
    "/lines/{line_id}",
    status_code=status.HTTP_200_OK,
)
def remove_line(
    line_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/lines/{line_id}",
    response_model=IdentifiedLine,
    status_code=status.HTTP_200_OK,
)
def view_line(
    line_id: UUID,
):
    pass


@router.get(
    "/lines",
    response_model=List[IdentifiedLine],
    status_code=status.HTTP_200_OK,
)
def list_lines(
    climd_id: Optional[UUID],
    image_id: Optional[UUID],
):
    pass
