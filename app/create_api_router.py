import os
from fastapi import APIRouter, Response, status, HTTPException, Query, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from uuid import UUID, uuid4
import io
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Dict, Union, Literal, Optional, Any
from datetime import datetime
from pydantic import BaseModel, create_model
from starlette.status import HTTP_403_FORBIDDEN, HTTP_409_CONFLICT

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


def rename(name):
    def decorator(fn):
        fn.__name__ = name
        return fn
    return decorator


class ItemBase(BaseModel):
    id: UUID  #= Field(default_factory=uuid4)
    user_id: str
    created: datetime  #= Field(default_factory=datetime.utcnow)


class VoteDefinition(BaseModel):
    model_name: str
    collection_name: str
    item_name: str
    type: Any  # TODO


def create_api_router(
    model_name: str,
    collection_name: str,
    item_name: str,
    statics: Dict[str, type] = dict(),
    voted: List[VoteDefinition] = list(),
):
    router = APIRouter(
        tags=[collection_name],
        dependencies=[Depends(auth.implicit_scheme)],
    )

    vote_in_models = {
        v.model_name: create_model(
            f"{v.model_name}In",
            value=(v.type, ...),
            public=(bool, ...),
            __base__=BaseModel,
        )
        for v in voted
    }

    vote_models = {
        v.model_name: create_model(
            v.model_name,
            id=(UUID, ...),
            user_id=(str, ...),
            created=(datetime, ...),
            __base__=vote_in_models[v.model_name],
        )
        for v in voted
    }

    MainModel = create_model(
        model_name,
        **{
            name: (t, ...)
            for name, t in statics.items()
        },
        **{
            v.collection_name: (List[vote_models[v.model_name]], ...)
            for v in voted
        },
        __base__=ItemBase,
    )

    MainModelIn = create_model(
        f"{model_name}In",
        **{
            name: (t, ...)
            for name, t in statics.items()
        },
    )

    @router.get(
        f"/{collection_name}",
        response_model=List[MainModel],
        status_code=status.HTTP_200_OK,
    )
    @rename(f"list_{collection_name}")
    def list_items(
        user: Auth0User = Security(guest_auth.get_user),
    ):
        # TODO: filters
        mongo_items = mongo.db[collection_name].find()

        return [
            MainModel(**mongo_item)
            for mongo_item in mongo_items
        ]

    @router.post(
        f"/{collection_name}",
        response_model=MainModel,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(auth.implicit_scheme)],
    )
    @rename(f"add_{item_name}")
    def add_item(
        model_in: MainModelIn,
        user: Auth0User = Security(auth.get_user),
    ):
        item = MainModel(
            id=uuid4(),
            user_id=user.id,
            created=datetime.utcnow(),
            **{v.collection_name: list() for v in voted},
        )
        mongo.db[collection_name].insert_one(item.dict())

        return item

    # TODO: need to create functions dynamically if we want custom argument names

    @router.get(
        f"/{collection_name}/{{item_id}}",
        response_model=MainModel,
        status_code=status.HTTP_200_OK,
    )
    @rename(f"view_{item_name}")
    def view_item(
        item_id: UUID,
        user: Auth0User = Security(guest_auth.get_user),
    ):
        mongo_item = mongo.db[collection_name].find_one(dict(id=item_id))

        if mongo_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {item_name} with that id")

        return MainModel(**mongo_item)

    # TODO: always have delete vote too?

    @router.delete(
        f"/{collection_name}/{{item_id}}",
        response_model=MainModel,
        status_code=status.HTTP_200_OK,
    )
    @rename(f"remove_{item_name}")
    def remove_item(
        item_id: UUID,
        user: Auth0User = Security(auth.get_user),
    ):
        pass

    for voted_item in voted:

        Vote = vote_models[voted_item.model_name]
        VoteIn = vote_in_models[voted_item.model_name]

        @router.post(
            f"/{collection_name}/{{item_id}}/{voted_item.collection_name}",
            response_model=Vote,
            status_code=status.HTTP_200_OK,
        )
        @rename(f"add_{voted_item.item_name}")
        def add_vote(
            item_id: UUID,
            vote: VoteIn,
            user: Auth0User = Security(auth.get_user),
        ):
            mongo_item = mongo.db[collection_name].find_one(dict(id=item_id))

            if mongo_item is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {item_name} with that id")

            if any([
                mongo_vote["user_id"] == user.id
                for mongo_vote in mongo_item[voted_item.collection_name]
            ]):
                print("conflict")
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already voted")

            new_vote = Vote(
                id=uuid4(),
                user_id=user.id,
                created=datetime.utcnow(),
                **vote.dict(),
            )

            mongo_item[voted_item.collection_name].append(new_vote.dict())

            mongo.db[collection_name].replace_one(dict(id=item_id), mongo_item)
            return new_vote

        @router.delete(
            f"/{collection_name}/{{item_id}}/{voted_item.collection_name}/{{vote_id}}",
            response_model=Vote,
            status_code=status.HTTP_200_OK,
        )
        @rename(f"remove_{voted_item.item_name}")
        def remove_vote(
            item_id: UUID,
            vote_id: UUID,
            user: Auth0User = Security(auth.get_user),
        ):
            mongo_item = mongo.db[collection_name].find_one(dict(id=item_id))

            if mongo_item is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {item_name} with that id")
   
            matched_votes = [
                mongo_vote
                for mongo_vote in mongo_item[voted_item.collection_name]
                if mongo_vote["id"] == vote_id
            ]
            if len(matched_votes) == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {voted_item.item_name} with that id")

            if matched_votes[0]["user_id"] != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Vote {voted_item.item_name} has another owner")
   
            mongo_item[voted_item.collection_name] = [
                mongo_vote
                for mongo_vote in mongo_item[voted_item.collection_name]
                if mongo_vote["id"] != vote_id
            ]

            mongo.db[collection_name].replace_one(dict(id=item_id), mongo_item)

        @router.put(
            f"/{collection_name}/{{item_id}}/{voted_item.collection_name}/{{vote_id}}",
            response_model=Vote,
            status_code=status.HTTP_200_OK,
        )
        @rename(f"update_{voted_item.item_name}")
        def update_vote(
            item_id: UUID,
            vote_id: UUID,
            vote: VoteIn,
            user: Auth0User = Security(auth.get_user),
        ):
            remove_response = remove_vote(item_id, vote_id, user)
            if remove_response.status_code == status.HTTP_200_OK:
                return add_vote(item_id, vote, user)
            else:
                return remove_response

    return router
