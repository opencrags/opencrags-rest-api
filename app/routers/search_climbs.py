from fastapi import APIRouter, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
import re
import io
from uuid import UUID
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Union, Literal, Optional, Any
import pymongo

from app import mongo, GeoPoint
from app.routers import sectors, climbs


router = APIRouter(
    tags=["utilities"],
)

# distance from point
# within area
# mean stars
# number of people who voted for stars?
# most voted grade
# number of people who voted for grade?
# number of ascents
# climb type

class SearchClimbsItem(BaseModel):
    sector_id: UUID
    climb_id: UUID
    distance: float
    name: str
    coordinates: GeoPoint


@router.get(
    "/search-climbs",
    response_model=List[Any],
    status_code=status.HTTP_200_OK,
)
def search_climbs(
    longitude: float,
    latitude: float,
    max_distance: float,  # km
    # sort_by: str
    limit: int = 16,
    offset: int = 0,
):
    mongo.db.sectors.create_index([("coordinate_votes.value", pymongo.GEOSPHERE)])

    mongo_climb_search = list(
        mongo.db.sectors.aggregate([
            {"$geoNear": {
                "includeLocs": "coordinate_votes.value",
                "distanceField": "distance",
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "maxDistance": max_distance * 1000,
                "distanceMultiplier": 0.001,
                "spherical": True,
                # query: can use query here
            }},
            {"$lookup": {
                "from": "climbs",
                "localField": "id",
                "foreignField": "sector_id",
                "as": "climb",
            }},
            {"$unwind": "$climb"},
            {"$skip": offset},
            {"$limit": limit},
        ])
    )

    return [
        SearchClimbsItem(
            sector_id=mongo_climb_search_item["id"],
            climb_id=mongo_climb_search_item["climb"]["id"],
            distance=mongo_climb_search_item["distance"],
            name=mongo_climb_search_item["climb"]["name_votes"][0]["value"],
            coordinates=mongo_climb_search_item["coordinate_votes"]["value"],
        )
        for mongo_climb_search_item in mongo_climb_search
        if (
            len(mongo_climb_search_item["climb"]["name_votes"]) >= 1
        )
    ]
