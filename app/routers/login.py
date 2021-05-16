import os
from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from typing import Optional

auth = Auth0(
    domain=os.environ["AUTH0_DOMAIN"],
    api_audience=os.environ["AUTH0_API_AUDIENCE"],
    auto_error=False,
    scope_auto_error=False,
)
router = APIRouter()


@router.get("/public")
def get_public():
    return {"message": "Anonymous user"}


@router.get("/secure", dependencies=[Depends(auth.implicit_scheme)])
def get_secure(
    user: Optional[Auth0User] = Security(auth.get_user)
):
    return {"message": f"{user}"}
