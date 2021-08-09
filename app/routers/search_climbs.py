from fastapi import APIRouter, Response, status, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
from fastapi_auth0 import Auth0, Auth0User
import re
import io
from uuid import UUID
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Tuple, Optional, Any
import pymongo

from app import mongo, GeoPoint
import os

from fastapi import APIRouter, Response, status
from uuid import UUID, uuid4
from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel

from app import mongo, routers

auth = Auth0(
    domain=os.environ["AUTH0_DOMAIN"],
    api_audience=os.environ["AUTH0_API_AUDIENCE"],
)

guest_auth = Auth0(
    domain=os.environ["AUTH0_DOMAIN"],
    api_audience=os.environ["AUTH0_API_AUDIENCE"],
    auto_error=False,
)

router = APIRouter(
    tags=["utilities"],
    dependencies=[Depends(auth.implicit_scheme)],
)


def censor_votes(mongo_votes, user):
    mongo_votes = mongo_votes.copy()
    return [
        vote
        if vote["public"] or (user is not None and vote["user_id"] == user.id)
        else (vote.update(user_id=None) or vote)
        for vote in mongo_votes
    ]


class SearchClimbsItem(BaseModel):
    sector_id: UUID
    climb_id: UUID
    distance: float
    name_votes: List[routers.climbs.vote_models["ClimbNameVote"]]
    grade_votes: List[routers.climbs.vote_models["GradeVote"]]
    rating_votes: List[routers.climbs.vote_models["RatingVote"]]
    coordinates: GeoPoint
    ascents: int


class SearchClimbsSort(str, Enum):
    distance = "distance"
    rating = "rating"


@router.post(
    "/search-climbs",
    response_model=List[SearchClimbsItem],
    status_code=status.HTTP_200_OK,
)
def search_climbs(
    longitude: float,
    latitude: float,
    max_distance: Optional[float] = None,  # km
    within_polygon: List[Tuple[float, float]] = None,
    grade_ids: Optional[List[UUID]] = None,
    minimum_grade_votes: Optional[int] = None,
    minimum_average_rating: Optional[float] = None,
    minimum_rating_votes: Optional[int] = None,
    minimum_ascents: Optional[int] = None,
    climb_types: Optional[List[routers.climbs.ClimbType]] = None,
    sort_by: Optional[SearchClimbsSort] = SearchClimbsSort.distance,
    limit: int = 16,
    offset: int = 0,
    user: Optional[Auth0User] = Security(guest_auth.get_user),
):
    mongo.db.sectors.create_index([("coordinate_votes.value", pymongo.GEOSPHERE)])

    pipeline = [
        {"$geoNear": {
            "includeLocs": "coordinate_votes.value",
            "distanceField": "distance",
            "near": {"type": "Point", "coordinates": [longitude, latitude]},
            "distanceMultiplier": 0.001,
            "spherical": True,
            # query: can use query here
        }},
    ]

    if max_distance is not None:
        pipeline[0]["$geoNear"]["maxDistance"] = max_distance * 1000

    if within_polygon is not None:
        pipeline.append({"$match": {
            "coordinate_votes.value": {
                "$geoWithin": {
                    "$geometry": {
                        "type": "Polygon",
                        "coordinates": [within_polygon],
                    }
                }
            }
        }})

    pipeline += [
        {"$lookup": {
            "from": "climbs",
            "localField": "id",
            "foreignField": "sector_id",
            "as": "climb",
        }}
    ]

    pipeline += [
        {"$unwind": "$climb"}
    ]

    if grade_ids is not None:
        pipeline += [
            {"$match": {"climb.most_voted_grade": {"$in": grade_ids}}}
        ]

    if minimum_grade_votes is not None:
        pipeline += [{"$match": {"$expr": {"$gte": [
            {"$size": "$climb.grade_votes"},
            minimum_grade_votes,
        ]}}}]

    if minimum_average_rating is not None:
        pipeline += [
            {"$match": {"climb.average_rating": {"$gte": minimum_average_rating}}}
        ]

    if minimum_rating_votes is not None:
        pipeline += [{"$match": {"$expr": {"$gte": [
            {"$size": "$climb.rating_votes"},
            minimum_rating_votes,
        ]}}}]

    if climb_types is not None:
        pipeline += [
            {"$match": {"climb.climb_type_votes.value": {"$in": climb_types}}}
        ]

    pipeline += [
        {"$lookup": {
            "from": "ascents",
            "localField": "climb.id",
            "foreignField": "climb_id",
            "as": "ascents",
        }},
        {"$set": {"ascents": {"$size": "$ascents"}}},
    ]

    if minimum_ascents is not None:
        pipeline += [
            {"$match": {"ascents": {"$gte": minimum_ascents}}}
        ]

    if sort_by == SearchClimbsSort.distance:
        pipeline += [{"$sort": {"distance": pymongo.ASCENDING}}]
    elif sort_by == SearchClimbsSort.average_rating:
        pipeline += [{"$sort": {"climb.average_rating": pymongo.DESCENDING}}]

    pipeline += [
        {"$skip": offset},
        {"$limit": limit},
    ]

    mongo_climb_search = list(mongo.db.sectors.aggregate(pipeline))

    return [
        SearchClimbsItem(
            sector_id=mongo_climb_search_item["id"],
            climb_id=mongo_climb_search_item["climb"]["id"],
            distance=mongo_climb_search_item["distance"],
            name_votes=censor_votes(mongo_climb_search_item["climb"]["name_votes"], user),
            grade_votes=censor_votes(mongo_climb_search_item["climb"]["grade_votes"], user),
            rating_votes=censor_votes(mongo_climb_search_item["climb"]["rating_votes"], user),
            coordinates=mongo_climb_search_item["coordinate_votes"]["value"],
            ascents=mongo_climb_search_item["ascents"],
        ).dict()
        for mongo_climb_search_item in mongo_climb_search
        if len(mongo_climb_search_item["climb"]["name_votes"]) >= 1
    ]
