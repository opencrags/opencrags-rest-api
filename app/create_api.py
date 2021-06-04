from fastapi import APIRouter, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
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

from app import mongo


def rename(name):
    def decorator(fn):
        fn.__name__ = name
        return fn
    return decorator


class ItemBase(BaseModel):
    id: UUID  #= Field(default_factory=uuid4)
    user_id: UUID
    created: datetime  #= Field(default_factory=datetime.utcnow)


class VoteDefinition(BaseModel):
    model_name: str
    collection_name: str
    item_name: str
    type: Any


def create_api(
    router,
    model_name: str,
    collection_name: str,
    item_name: str,
    statics: Dict[str, type] = dict(),
    voted: List[VoteDefinition] = list(),
):

    vote_models = {
        v.model_name: create_model(
            v.model_name,
            value=(v.type, ...),
            __base__=ItemBase,
        )
        for v in voted
    }

    vote_in_models = {
        v.model_name: create_model(
            f"{v.model_name}In",
            value=(v.type, ...),
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
        __base__=ItemBase,
    )

    @router.get(
        f"/{collection_name}",
        response_model=List[MainModel],
        status_code=status.HTTP_200_OK,
    )
    @rename(f"list_{collection_name}")
    def list_items():
        # TODO: filters
        mongo_items = mongo.db[collection_name].find()

        return [
            MainModel(**mongo_item)
            for mongo_item in mongo_items
        ]

    @router.post(
        f"/{collection_name}",
        response_model=MainModel,
        status_code=status.HTTP_200_OK,
    )
    @rename(f"add_{item_name}")
    def add_item(
        model_in: MainModelIn
    ):
        item = MainModel(
            id=uuid4(),
            user_id=uuid4(), # TODO
            created=datetime.utcnow(),
            **{v.model_name: list() for v in voted},
        )
        mongo.db[collection_name].save(item.dict())

        return item 

    # TODO: need to create functions dynamically if we want custom argument names

    @router.get(
        f"/{collection_name}/{{item_id}}",
        response_model=List[MainModel],
        status_code=status.HTTP_200_OK,
    )
    @rename(f"view_{item_name}")
    def view_item(
        item_id: UUID,
    ):
        mongo_item = mongo.db[collection_name].find_one(dict(id=id))

        if mongo_item is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        else:
            return MainModel(**mongo_item)

    # TODO: always have delete vote too?

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
        ):
            pass

        @router.put(
            f"/{collection_name}/{{item_id}}/{voted_item.collection_name}/{{vote_id}}",
            response_model=Vote,
            status_code=status.HTTP_200_OK,
        )
        @rename(f"update_{voted_item.item_name}")
        def add_vote(
            item_id: UUID,
            vote_id: UUID,
            vote: VoteIn,
        ):
            pass

