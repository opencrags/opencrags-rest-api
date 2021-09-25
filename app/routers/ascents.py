
import os
from fastapi import APIRouter, status, HTTPException, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from uuid import UUID, uuid4
from pydantic import BaseModel
import typing
from typing import List, Dict, Union, Optional, Any, get_type_hints
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, conint, create_model

from app import mongo


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
    tags=["ascents"],
    dependencies=[Depends(auth.implicit_scheme)],
)


class AscentType(str, Enum):
    flash = "flash"
    onsight = "onsight"
    pinkpoint = "pinkpoint"
    redpoint = "redpoint"


class AscentIn(BaseModel):
    climb_id: UUID
    ascent_date: datetime
    ascent_type: Optional[AscentType]
    attempts: Optional[conint(ge=1)]
    description: Optional[str]
    public: bool


class Ascent(AscentIn):
    id: UUID
    user_id: Optional[str]
    created: datetime


class AscentUpdate(BaseModel):
    ascent_date: datetime
    ascent_type: Optional[AscentType]
    attempts: Optional[conint(ge=1)]
    description: Optional[str]
    public: bool


def censor_ascent(mongo_ascent, user):
    return {
        key: value if (
            key != "user_id"
            or mongo_ascent["public"]
            or user.id == mongo_ascent["user_id"]
        ) else None
        for key, value in mongo_ascent.items()
    }


AscentQuery = create_model(
    "AscentQuery",
    **{
        name: (Optional[field.type_], None)
        for name, field in Ascent.__fields__.items()
    },
)


@router.post(
    "/ascents/query",
    response_model=List[Ascent],
    status_code=status.HTTP_200_OK,
)
def query_ascents(
    query: AscentQuery,
    limit: Optional[conint(ge=1, le=100)] = 20,
    offset: Optional[conint(ge=0)] = 0,
    user: Optional[Auth0User] = Security(guest_auth.get_user),
):
    mongo_items = (
        mongo.db.ascents
        .find(query.dict(exclude_none=True))
        .skip(offset)
        .limit(limit)
    )
    return [
        Ascent(**censor_ascent(mongo_item, user))
        for mongo_item in mongo_items
    ]


@router.post(
    f"/ascents",
    response_model=Ascent,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth.implicit_scheme)],
)
def add_ascent(
    ascent_in: AscentIn,
    user: Auth0User = Security(auth.get_user),
):
    mongo.db.ascents.create_index("id", unique=True)

    item = Ascent(
        id=uuid4(),
        user_id=user.id,
        created=datetime.utcnow(),
        **ascent_in.dict(),
    )
    mongo.db.ascents.insert_one(item.dict())

    return item


@router.get(
    "/ascents/{item_id}",
    response_model=Ascent,
    status_code=status.HTTP_200_OK,
)
def view_ascent(
    item_id: UUID,
    user: Auth0User = Security(guest_auth.get_user),
):
    mongo_item = mongo.db.ascents.find_one(dict(id=item_id))

    if mongo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No ascent with that id")

    return Ascent(**censor_ascent(mongo_item, user))


@router.delete(
    "/ascents/{item_id}",
    response_model=Ascent,
    status_code=status.HTTP_200_OK,
)
def remove_ascent(
    item_id: UUID,
    user: Auth0User = Security(auth.get_user),
):
    mongo_item = mongo.db.ascents.find_one(dict(id=item_id))

    if mongo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ascent with that id")

    if mongo_item["user_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ascent has another owner")

    mongo_item = mongo.db.ascents.find_one_and_delete(dict(id=item_id))

    if mongo_item is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove ascent")

    return Ascent(**mongo_item)


@router.put(
    "/ascents/{item_id}",
    response_model=Ascent,
    status_code=status.HTTP_200_OK,
)
def update_ascent(
    item_id: UUID,
    ascent_update: AscentUpdate,
    user: Auth0User = Security(auth.get_user),
):
    mongo_item = mongo.db.ascents.find_one(dict(id=item_id))

    if mongo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ascent with that id")

    if mongo_item["user_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ascent has another owner")

    mongo_item.update(**ascent_update.dict())
    item = Ascent(**mongo_item)
    mongo.db.ascents.find_one_and_replace(dict(id=item_id), item.dict())

    return Ascent(**item.dict())
