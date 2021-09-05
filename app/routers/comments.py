
import os
from fastapi import APIRouter, status, HTTPException, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from uuid import UUID, uuid4
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, get_type_hints, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, conint, constr

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
    tags=["comments"],
    dependencies=[Depends(auth.implicit_scheme)],
)


class CommentIn(BaseModel):
    related_ids: List[UUID]
    comment: constr(min_length=1)


class Comment(CommentIn):
    id: UUID
    user_id: str
    created: datetime


class CommentUpdate(BaseModel):
    comment: constr(min_length=1)


@router.get(
    "/comments",
    response_model=List[Comment],
    status_code=status.HTTP_200_OK,
)
def filter_comments(
    related_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    limit: Optional[conint(ge=1, le=100)] = 20,
    offset: Optional[conint(ge=0)] = 0,
    user: Optional[Auth0User] = Security(guest_auth.get_user),
):
    mongo.db.comments.create_index("related_ids")

    query = dict()
    if related_id is not None:
        query["related_ids"] = related_id

    if user_id is not None:
        query["user_id"] = user_id

    mongo_items = mongo.db.comments.find(query).skip(offset).limit(limit)

    return [
        Comment(**mongo_item)
        for mongo_item in mongo_items
    ]


@router.post(
    f"/comments",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth.implicit_scheme)],
)
def add_comment(
    comment_in: CommentIn,
    user: Auth0User = Security(auth.get_user),
):
    mongo.db.comments.create_index("id", unique=True)
    comment_in.related_ids = list(set(comment_in.related_ids))

    item = Comment(
        id=uuid4(),
        user_id=user.id,
        created=datetime.utcnow(),
        **comment_in.dict(),
    )
    mongo.db.comments.insert_one(item.dict())

    return item


@router.get(
    "/comments/{item_id}",
    response_model=Comment,
    status_code=status.HTTP_200_OK,
)
def view_comment(
    item_id: UUID,
    user: Auth0User = Security(guest_auth.get_user),
):
    mongo_item = mongo.db.comments.find_one(dict(id=item_id))

    if mongo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No comment with that id")

    return Comment(**mongo_item)


@router.delete(
    "/comments/{item_id}",
    response_model=Comment,
    status_code=status.HTTP_200_OK,
)
def remove_comment(
    item_id: UUID,
    user: Auth0User = Security(auth.get_user),
):
    mongo_item = mongo.db.comments.find_one(dict(id=item_id))

    if mongo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comment with that id")

    if mongo_item["user_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Comment has another owner")

    mongo_item = mongo.db.comments.find_one_and_delete(dict(id=item_id))

    if mongo_item is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove comment")

    return Comment(**mongo_item)


@router.put(
    "/comments/{item_id}",
    response_model=Comment,
    status_code=status.HTTP_200_OK,
)
def update_comment(
    item_id: UUID,
    comment_update: CommentUpdate,
    user: Auth0User = Security(auth.get_user),
):
    mongo_item = mongo.db.comments.find_one(dict(id=item_id))

    if mongo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comment with that id")

    if mongo_item["user_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Comment has another owner")

    mongo_item.update(**comment_update.dict())
    item = Comment(**mongo_item)
    mongo.db.comments.find_one_and_replace(dict(id=item_id), item.dict())

    return Comment(**item.dict())
