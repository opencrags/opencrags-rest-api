import os
from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
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
from typing import List, Dict, Union, Literal, Optional, Any
from datetime import datetime
from pydantic import BaseModel, create_model
from starlette.status import HTTP_401_UNAUTHORIZED

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
    tags=["users"],
)


class UserIn(BaseModel):
    display_name: Optional[str]


class User(UserIn):
    id: str


@router.post(
    "/users",
    response_model=User,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def add_user_info(
    user: UserIn,
    auth0User: Optional[Auth0User] = Security(auth.get_user)
):
    user = User(
        id=auth0User.id,
        **user.dict(),
    )
    mongo.db.users.insert_one(user.dict())
    return user


@router.get(
    "/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def view_user_info(
    user_id: str,
    auth0User: Optional[Auth0User] = Security(guest_auth.get_user)
):
    mongo_user = mongo.db.users.find_one(dict(id=user_id))

    if mongo_user is None:
        return User(id=user_id, display_name=None)
    else:
        return User(**mongo_user)


@router.put(
    "/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def update_user_info(
    user_id: str,
    user: UserIn,
    auth0User: Optional[Auth0User] = Security(auth.get_user)
):
    if auth0User.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not allowed to update other users' settings")

    update_result = mongo.db.users.update_one(
        dict(id=user_id),
        {"$set": {"display_name": user.display_name}},
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unable to find user")

    return mongo.db.users.find_one(dict(id=user_id))
