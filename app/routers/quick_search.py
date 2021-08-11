from fastapi import APIRouter, Response, status, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
from fastapi_auth0 import Auth0, Auth0User
import os
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
from app.routers import (
    crags,
    sectors,
    climbs,
)

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


def censor_mongo_item(mongo_item, user):
    print("censor", flush=True)
    mongo_item = mongo_item.copy()
    return {
        key: censor_votes(value, user) if "votes" in key else value
        for key, value in mongo_item.items()
    }


class QuickSearchResultItemType(str, Enum):
    crag = "crag"
    sector = "sector"
    climb = "climb"


class QuickSearchResultItem(BaseModel):
    type: QuickSearchResultItemType
    crag: Optional[crags.MainModel]
    sector: Optional[sectors.MainModel]
    climb: Optional[climbs.MainModel]


@router.get(
    "/quick-search",
    response_model=List[QuickSearchResultItem],
    status_code=status.HTTP_200_OK,
)
def search_crags_sectors_and_climbs_by_name(
    text: str,
    limit: int = 16,
    offset: int = 0,
    user: Optional[Auth0User] = Security(guest_auth.get_user),
):  
    pattern = re.compile(f".*{text}.*", re.IGNORECASE)
    mongo_crags = list(mongo.db.crags.find({"name_votes.value": {"$regex": pattern}}).skip(offset).limit(limit))

    results = [
        QuickSearchResultItem(
            type=QuickSearchResultItemType.crag,
            crag=censor_mongo_item(mongo_crag, user),
        )
        for mongo_crag in mongo_crags
    ]

    offset = max(0, offset - len(mongo_crags))
    limit -= len(mongo_crags)
    if limit >= 1:
        mongo_sectors = list(mongo.db.sectors.find({"name_votes.value": {"$regex": pattern}}).skip(offset).limit(limit))

        results += [
            QuickSearchResultItem(
                type=QuickSearchResultItemType.sector,
                sector=censor_mongo_item(mongo_sector, user),
            )
            for mongo_sector in mongo_sectors
        ]
        offset = max(0, offset - len(mongo_sectors))
        limit -= len(mongo_sectors)

    if limit >= 1:
        mongo_climbs = list(mongo.db.climbs.find({"name_votes.value": {"$regex": pattern}}).skip(offset).limit(limit))
        results += [
            QuickSearchResultItem(
                type=QuickSearchResultItemType.climb,
                climb=censor_mongo_item(mongo_climb, user),
            )
            for mongo_climb in mongo_climbs
        ]

    return results
