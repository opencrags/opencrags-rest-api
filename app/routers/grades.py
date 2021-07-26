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
    rank: int


@router.get(
    "/grade-system-grades",
    response_model=List[GradeSystemGrade],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth.implicit_scheme)],
)
def list_grade_systems_with_grades(
    system: Optional[str] = None,
    grade: Optional[str] = None,
    user: Optional[Auth0User] = Security(guest_auth.get_user)
):
    filters = dict()
    if system:
        filters["grade"] = system
    if grade:
        filters["grade"] = grade
    return [
        GradeSystemGrade(**mongo_grade_system_grade)
        for mongo_grade_system_grade in mongo.db.grade_system_grades.find(filters)
    ]


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


def add_grades():
    system_grades = {
        "Fontainebleau": [
            "1",
            "2",
            "3",
            "4",
            "4+",
            "5",
            "5+",
            "6A+",
            "6B",
            "6B+",
            "6C",
            "6C+",
            "7A	",
            "7A+",
            "7B",
            "7B+",
            "7C",
            "7C+",
            "8A",
            "8A+",
            "8B",
            "8B+",
            "8C",
            "8C+",
            "9A",
            "9A+",
            "9B",
            "9B+",
            "9C",
            "9C+",
        ],
        "Hueco": [
            "VB",
            "V0",
            "V0+",
            "V1",
            "V2",
            "V3",
            "V4",
            "V5",
            "V6",
            "V7",
            "V8",
            "V9",
            "V10",
            "V11",
            "V12",
            "V13",
            "V14",
            "V15",
            "V16",
            "V17",
            "V18",
            "V19",
            "V20",
        ],
    }

    for system, grades in system_grades.items():
        for index, grade in enumerate(grades):
            mongo.db.grade_system_grades.insert_one(GradeSystemGrade(
                id=uuid4(),
                system=system,
                grade=grade,
                rank=index,
            ).dict())

if mongo.db.grade_system_grades.count() == 0:
    add_grades()
