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
from enum import Enum
from typing import List, Dict, Union, Literal, Optional, Any
from datetime import datetime
from pydantic import BaseModel, create_model

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
    tags=["grade-system-grades"],
)


class GradeSystemGrade(BaseModel):
    id: UUID
    system: str
    grade: str


@router.get(
    f"/grade-system-grades",
    response_model=List[GradeSystemGrade],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def list_grade_systems_with_grades(
    system: Optional[str] = None,
    grade: Optional[str] = None,
    user: Optional[Auth0User] = Security(guest_auth.get_user)
):
    mongo_items = mongo.db.grade_system_grades.find(dict(
        system=system,
        grade=grade,
    ))
    return mongo_items


@router.get(
    "/grade-system-grades/{grade_system_grade_id}",
    response_model=GradeSystemGrade,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def view_grade_system_grade(
    grade_system_grade_id: UUID,
    user: Optional[Auth0User] = Security(guest_auth.get_user)
):
    mongo_item = mongo.db.grade_system_grades.find_one(dict(id=grade_system_grade_id))

    if mongo_item is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return mongo_item
