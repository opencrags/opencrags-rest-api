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

from app.items.rating import Rating, RatingId, IdentifiedRating


router = APIRouter(
    tags=["ratings"],
)


@router.post(
    "/ratings",
    response_model=RatingId,
    status_code=status.HTTP_201_CREATED,
)
def add_rating(
    climb_id: UUID,
    rating: Rating,
):
    rating_id = UUID(int=random.getrandbits(128))
    return RatingId(id=rating_id)



@router.put(
    "/ratings/{rating_id}",
    response_model=IdentifiedRating,
    status_code=status.HTTP_200_OK,
)
def update_rating(
    climb_id: UUID,
    rating_id: UUID,
    rating: Rating,
):
    pass


@router.delete(
    "/ratings/{rating_id}",
    status_code=status.HTTP_200_OK,
)
def remove_vote(
    climb_id: UUID,
    rating_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/ratings/{rating_id}",
    response_model=IdentifiedRating,
    status_code=status.HTTP_200_OK,
)
def view_vote(
    climb_id: UUID,
    rating_id: UUID,
):
    pass


@router.get(
    "/ratings",
    response_model=List[IdentifiedRating],
    status_code=status.HTTP_200_OK,
)
def list_public_ratings(
    climd_id: UUID,
):
    pass


@router.get(
    "/ratings/summary",
    # response_model=List[IdentifiedRating],
    status_code=status.HTTP_200_OK,
    description="Includes private votes",
)
def summary_of_private_and_public_ratings(
    climd_id: UUID,
):
    pass
