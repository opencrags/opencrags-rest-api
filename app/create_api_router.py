import os
from fastapi import APIRouter, status, HTTPException, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from uuid import UUID, uuid4
from pydantic import BaseModel
import typing
from typing import List, Dict, Union, Optional, Any, Callable, get_type_hints
from datetime import datetime
from pydantic import BaseModel, create_model, conint

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


def is_optional(t):
    return (
        typing.get_origin(t) is Union
        and type(None) in typing.get_args(t)
    )


class ItemBase(BaseModel):
    id: UUID
    user_id: str
    created: datetime
    updated: datetime


class VoteAggregation(BaseModel):
    fn: Callable[[List], Any]
    name: str
    type: Any

class VoteDefinition(BaseModel):
    model_name: str
    collection_name: str
    item_name: str
    type: Any
    aggregation: Optional[VoteAggregation]


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
            user_id=(Optional[str], None),
            created=(datetime, ...),
            __base__=vote_in_models[v.model_name],
        )
        for v in voted
    }

    MainModel = create_model(
        model_name,
        **{
            name: (t, None) if is_optional(t) else (t, ...)
            for name, t in statics.items()
        },
        **{
            v.collection_name: (List[vote_models[v.model_name]], ...)
            for v in voted
        },
        **{
            v.aggregation.name: (Optional[v.aggregation.type], None)
            for v in voted
            if v.aggregation is not None
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

    Query = create_model(
        f"{model_name}Query",
        **{
            name: (Optional[field.type_], None)
            for name, field in MainModel.__fields__.items()
        },
    )

    def censor_item(mongo_item, user):
        mongo_item = mongo_item.copy()
        mongo_item.update(**{
            v.collection_name: [
                vote
                if vote["public"] or (user is not None and vote["user_id"] == user.id)
                else (vote.update(user_id=None) or vote)
                for vote in mongo_item[v.collection_name]
            ]
            for v in voted
        })
        return mongo_item

    @router.post(
        f"/{collection_name}/query",
        response_model=List[MainModel],
        status_code=status.HTTP_200_OK,
    )
    @rename(f"query_{collection_name}")
    def query_collection(
        query: Query,
        limit: Optional[conint(ge=1, le=100)] = 20,
        offset: Optional[conint(ge=0)] = 0,
        user: Optional[Auth0User] = Security(guest_auth.get_user),
    ):
        mongo_items = (
            mongo.db[collection_name]
            .find(query.dict(exclude_none=True))
            .skip(offset)
            .limit(limit)
        )

        return [
            MainModel(**censor_item(mongo_item, user))
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
        mongo.db[collection_name].create_index("id", unique=True)

        item = MainModel(
            id=uuid4(),
            user_id=user.id,
            created=datetime.utcnow(),
            updated=datetime.utcnow(),
            **model_in.dict(),
            **{v.collection_name: list() for v in voted},
        )
        mongo.db[collection_name].insert_one(item.dict())

        return item

    @router.put(
        f"/{collection_name}/{{item_id}}",
        response_model=MainModel,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(auth.implicit_scheme)],
    )
    @rename(f"update_{item_name}")
    def update_item(
        item_id: UUID,
        model_in: MainModelIn,
        user: Auth0User = Security(auth.get_user),
    ):
        mongo_item = mongo.db[collection_name].find_one(dict(id=item_id))

        if mongo_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {item_name} with that id")

        if mongo_item["user_id"] != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Item {item_name} has another owner")

        mongo_item.update(**model_in.dict())
        mongo_item.update(updated=datetime.utcnow())
        mongo.db[collection_name].replace_one({"id": item_id}, mongo_item)
        return mongo_item

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

        return MainModel(**censor_item(mongo_item, user))

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
        mongo_item = mongo.db[collection_name].find_one(dict(id=item_id))

        if mongo_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {item_name} with that id")

        if mongo_item["user_id"] != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Item {item_name} has another owner")

        # TODO: should not allow deletion if there is related content owned by other users?

        mongo_item = mongo.db[collection_name].find_one_and_delete(dict(id=item_id))

        if mongo_item is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove {item_name}")

        return MainModel(**censor_item(mongo_item, user))


    def create_vote_api(voted_item):
        Vote = vote_models[voted_item.model_name]
        VoteIn = vote_in_models[voted_item.model_name]

        def update_aggregation(item_id):
            mongo_item = mongo.db[collection_name].find_one(dict(id=item_id))
            aggregated_value = voted_item.aggregation.fn(mongo_item[voted_item.collection_name])
            mongo.db[collection_name].update_one(dict(id=item_id), {"$set": {voted_item.aggregation.name: aggregated_value}})

        @router.post(
            f"/{collection_name}/{{item_id}}/{voted_item.collection_name}",
            response_model=Vote,
            status_code=status.HTTP_201_CREATED,
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
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already voted")

            new_vote = Vote(
                id=uuid4(),
                user_id=user.id,
                created=datetime.utcnow(),
                **vote.dict(),
            )

            mongo.db[collection_name].update_one(dict(id=item_id), {"$push": {voted_item.collection_name: new_vote.dict()}})
            if voted_item.aggregation is not None:
                update_aggregation(item_id)
            return new_vote

        @router.delete(
            f"/{collection_name}/{{item_id}}/{voted_item.collection_name}/{{vote_id}}",
            response_model=dict,
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

            update_result = mongo.db[collection_name].update_one(dict(id=item_id), {"$pull": {voted_item.collection_name: {"id": vote_id}}})

            if update_result.modified_count == 0:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove vote")

            if voted_item.aggregation is not None:
                update_aggregation(item_id)

            return {}

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
            remove_vote(item_id, vote_id, user)
            return add_vote(item_id, vote, user)

    for voted_item in voted:
        create_vote_api(voted_item)

    return router, MainModel, vote_models
