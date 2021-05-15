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

from app.items.climb import Climb, ClimbId, IdentifiedClimb


router = APIRouter(
    tags=["climbs"],
)


@router.post(
    "/climbs",
    response_model=Climb,
    status_code=status.HTTP_201_CREATED,
)
def add_climb(
    climb: Climb,
):
    climb_id = UUID(int=random.getrandbits(128))
    return ClimbId(id=climb_id)



@router.put(
    "/climbs/{climb_id}",
    response_model=IdentifiedClimb,
    status_code=status.HTTP_200_OK,
)
def update_climb(
    climb_id: UUID,
    climb: Climb,
):
    pass


@router.delete(
    "/climbs/{climb_id}",
    status_code=status.HTTP_200_OK,
)
def remove_climb(
    climb_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/climbs/{climb_id}",
    response_model=IdentifiedClimb,
    status_code=status.HTTP_200_OK,
)
def view_climb(
    climb_id: UUID,
):
    pass


class ClimbType(str, Enum):
    any = "any"
    boulder = "boulder"
    route = "route"

class SortBy(str, Enum):
    distance = "distance"
    grade = "grade"
    stars = "stars"
    ascents = "ascents"

class SortOrder(str, Enum):
    ascending = "ascending"
    descending = "descending"

@router.get(
    "/climbs",
    response_model=List[Climb],
    status_code=status.HTTP_200_OK,
)
def list_climbs_using_many_filters(
    type: ClimbType,
    min_grade: str = "4",
    max_grade: str = "9C",
    min_stars: float = Query(0, ge=0, le=5),
    max_stars: float = Query(5, ge=0, le=5),
    min_ascents: int = Query(0, ge=0),
    max_ascents: int = Query(999999, ge=0),
    location: str = Query(...),
    min_distance: float = Query(0, ge=0),
    max_distance: float = Query(100, ge=0),
    sort_by: SortBy = Query(SortBy.distance),
    sort_order: SortOrder = Query(SortOrder.ascending),
    start: int = 0,
    limit: int = Query(20, le=100),
):
    pass
