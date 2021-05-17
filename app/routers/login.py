import os
from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from typing import Optional

auth = Auth0(
    domain=os.environ["AUTH0_DOMAIN"],
    api_audience=os.environ["AUTH0_API_AUDIENCE"],
)
guest_auth = Auth0(
    domain=os.environ["AUTH0_DOMAIN"],
    api_audience=os.environ["AUTH0_API_AUDIENCE"],
    auto_error=False,
)

router = APIRouter()


@router.get("/secure", dependencies=[Depends(auth.implicit_scheme)])
def get_secure(
    user: Optional[Auth0User] = Security(guest_auth.get_user)
):
    if user is None:
       return {"message": "public user"}
    
    return {"message": f"private user {user}"}
