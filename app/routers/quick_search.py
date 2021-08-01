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
from typing import List, Union, Literal, Optional

from app import mongo


router = APIRouter(
    tags=["utilities"],
)


class QuickSearchResultItemType(str, Enum):
    crag = "crag"
    sector = "sector"
    climb = "climb"


class QuickSearchResultItem(BaseModel):
    type: QuickSearchResultItemType
    id: UUID
    name: str


@router.get(
    "/quick-search",
    response_model=List[QuickSearchResultItem],
    status_code=status.HTTP_200_OK,
)
def search_crags_sectors_and_climbs_by_name(
    text: str,
    limit: int = 16,
    offset: int = 0,
):  
    pattern = re.compile(f"{text}", re.IGNORECASE)
    mongo_crags = list(mongo.db.crags.find({"name_votes.value": { "$regex": pattern}}).skip(offset).limit(limit))

    results = [
        QuickSearchResultItem(
            type=QuickSearchResultItemType.crag,
            id=mongo_crag["id"],
            name=[
                name_vote["value"]
                for name_vote in mongo_crag["name_votes"]
                if pattern.match(name_vote["value"])
            ][0],
        )
        for mongo_crag in mongo_crags
    ]

    offset = max(0, offset - len(mongo_crags))
    limit -= len(mongo_crags)
    if limit >= 1:
        mongo_sectors = list(mongo.db.sectors.find({"name_votes.value": { "$regex": pattern}}).skip(offset).limit(limit))
        results += [
            QuickSearchResultItem(
                type=QuickSearchResultItemType.sector,
                id=mongo_sector["id"],
                name=[
                    name_vote["value"]
                    for name_vote in mongo_sector["name_votes"]
                    if pattern.match(name_vote["value"])
                ][0],
            )
            for mongo_sector in mongo_sectors
        ]
        offset = max(0, offset - len(mongo_sectors))
        limit -= len(mongo_sectors)

    if limit >= 1:
        mongo_climbs = list(mongo.db.climbs.find({"name_votes.value": { "$regex": pattern}}).skip(offset).limit(limit))
        results += [
            QuickSearchResultItem(
                type=QuickSearchResultItemType.climb,
                id=mongo_climb["id"],
                name=[
                    name_vote["value"]
                    for name_vote in mongo_climb["name_votes"]
                    if pattern.match(name_vote["value"])
                ][0],
            )
            for mongo_climb in mongo_climbs
        ]

    return results
