
import os
from fastapi import APIRouter, status, HTTPException, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from uuid import UUID, uuid4
from pydantic import BaseModel
from typing import List, Dict, Optional, List
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


class CommentRelatedType(str, Enum):
    crag = "crag"
    sector = "sector"
    climb = "climb"


class CommentIn(BaseModel):
    related_id: UUID
    related_type: CommentRelatedType
    comment: constr(min_length=1)


class ReplyIn(BaseModel):
    comment_id: UUID
    reply: constr(min_length=1)


class Reply(ReplyIn):
    id: UUID
    user_id: str
    created: datetime
    last_edited: datetime


class Comment(CommentIn):
    id: UUID
    all_related_ids: List[UUID]
    user_id: str
    created: datetime
    last_edited: datetime
    last_activity: datetime
    replies: List[Reply]


class CommentUpdate(BaseModel):
    comment: constr(min_length=1)


class ReplyUpdate(BaseModel):
    reply: constr(min_length=1)


@router.get(
    "/comments",
    response_model=List[Comment],
    status_code=status.HTTP_200_OK,
)
def filter_comments(
    related_id: Optional[UUID] = None,
    related_type: CommentRelatedType = None,
    limit: Optional[conint(ge=1, le=100)] = 20,
    offset: Optional[conint(ge=0)] = 0,
    user: Optional[Auth0User] = Security(guest_auth.get_user),
):
    mongo.db.comments.create_index("all_related_ids")

    query = dict()
    if related_id is not None:
        query["all_related_ids"] = related_id

    if related_type is not None:
        query["related_type"] = related_type

    mongo_items = mongo.db.comments.find(query).skip(offset).limit(limit)

    return [
        Comment(**mongo_item)
        for mongo_item in mongo_items
    ]


@router.post(
    "/comments",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth.implicit_scheme)],
)
def add_comment(
    comment_in: CommentIn,
    user: Auth0User = Security(auth.get_user),
):
    mongo.db.comments.create_index("id", unique=True)

    if comment_in.related_type == CommentRelatedType.crag:
        mongo_crag = mongo.db.crags.find_one(dict(id=comment_in.related_id))
        if mongo_crag is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crag {comment_in.related_id} not found",
            )
        all_related_ids = [comment_in.related_id]
    elif comment_in.related_type == CommentRelatedType.sector:
        mongo_sector = mongo.db.sectors.find_one(dict(id=comment_in.related_id))
        if mongo_sector is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sector {comment_in.related_id} not found",
            )
        all_related_ids = [
            mongo_sector["crag_id"],
            comment_in.related_id,
        ]
    elif comment_in.related_type == CommentRelatedType.climb:
        mongo_climb = mongo.db.climbs.find_one(dict(id=comment_in.related_id))
        if mongo_climb is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Climb {comment_in.related_id} not found",
            )
        all_related_ids = [
            mongo_climb["crag_id"],
            mongo_climb["sector_id"],
            comment_in.related_id,
        ]

    item = Comment(
        id=uuid4(),
        all_related_ids=all_related_ids,
        user_id=user.id,
        created=datetime.utcnow(),
        last_edited=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        replies=list(),
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No comment with id {item_id}")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No comment with id {item_id}")

    if mongo_item["user_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Comment has another owner")

    if len(mongo_item["replies"]) >= 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Comment has replies and cannot be deleted")

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
    mongo_item.update(dict(
        last_edited=datetime.utcnow(),
        last_activity=datetime.utcnow(),
    ))
    item = Comment(**mongo_item)
    mongo.db.comments.find_one_and_replace(dict(id=item_id), item.dict())

    return Comment(**item.dict())


@router.post(
    "/comments/{item_id}/replies",
    response_model=Reply,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth.implicit_scheme)],
)
def add_reply(
    item_id: UUID,
    reply_in: ReplyIn,
    user: Auth0User = Security(auth.get_user),
):
    mongo_comment = mongo.db.comments.find_one(dict(id=item_id))

    if mongo_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comment with that id")

    reply = Reply(
        id=uuid4(),
        user_id=user.id,
        created=datetime.utcnow(),
        last_edited=datetime.utcnow(),
        **reply_in.dict(),
    )
    mongo_comment["replies"].append(reply.dict())
    mongo_comment.update(**dict(
        last_activity=datetime.utcnow(),
    ))
    mongo.db.comments.find_one_and_replace(dict(id=item_id), mongo_comment)
    return reply


@router.get(
    "/comments/{item_id}/replies/{reply_id}",
    response_model=Reply,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def view_reply(
    item_id: UUID,
    reply_id: UUID,
    user: Auth0User = Security(auth.get_user),
):
    mongo_comment = mongo.db.comments.find_one(dict(id=item_id))

    if mongo_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comment with that id")

    reply_ids = [mongo_reply["id"] for mongo_reply in mongo_comment["replies"]]
    if reply_id not in reply_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No reply with that id")

    index = reply_ids.index(reply_id)
    return mongo_comment["replies"][index]


@router.delete(
    "/comments/{item_id}/replies/{reply_id}",
    response_model=Reply,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def delete_reply(
    item_id: UUID,
    reply_id: UUID,
    user: Auth0User = Security(auth.get_user),
):
    mongo_comment = mongo.db.comments.find_one(dict(id=item_id))

    if mongo_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comment with that id")

    reply_ids = [mongo_reply["id"] for mongo_reply in mongo_comment["replies"]]
    if reply_id not in reply_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No reply with that id")

    if reply_ids.index(reply_id) < len(mongo_comment["replies"]) - 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reply has replies and cannot be deleted")

    mongo_reply = mongo_comment["replies"].pop(-1)
    mongo_comment.update(**dict(
        last_activity=datetime.utcnow(),
    ))
    mongo.db.comments.find_one_and_replace(dict(id=item_id), mongo_comment)

    return mongo_reply


@router.put(
    "/comments/{item_id}/replies/{reply_id}",
    response_model=Reply,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def update_reply(
    item_id: UUID,
    reply_id: UUID,
    reply_update: ReplyUpdate,
    user: Auth0User = Security(auth.get_user),
):
    mongo_comment = mongo.db.comments.find_one(dict(id=item_id))

    if mongo_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comment with that id")

    reply_ids = [mongo_reply["id"] for mongo_reply in mongo_comment["replies"]]
    if reply_id not in reply_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No reply with that id")

    index = reply_ids.index(reply_id)
    mongo_comment["replies"][index].update(
        last_edited=datetime.utcnow(),
        **reply_update.dict(),
    )
    mongo_comment.update(**dict(
        last_activity=datetime.utcnow(),
    ))
    mongo.db.comments.find_one_and_replace(dict(id=item_id), mongo_comment)

    return mongo_comment["replies"][index]
