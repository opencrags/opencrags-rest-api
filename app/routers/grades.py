import os
from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0, Auth0User
from fastapi import APIRouter, Response, status
from uuid import UUID, uuid4
from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel

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
        "Fontainebleau grading system": [
            "1",
            "2",
            "3",
            "4",
            "4+",
            "5",
            "5+",
            "6A",
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
        "Hueco scale": [
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
        "French numerical system": [
            "1",
            "2",
            "3",
            "4a",
            "4b",
            "4c",
            "5a",
            "5b",
            "5c",
            "6a",
            "6a+",
            "6b",
            "6b+",
            "6c",
            "6c+",
            "7a	",
            "7a+",
            "7b",
            "7b+",
            "7c",
            "7c+",
            "8a",
            "8a+",
            "8b",
            "8b+",
            "8c",
            "8c+",
            "9a",
            "9a+",
            "9b",
            "9b+",
            "9c",
            "9c+",
        ],
        "Yosemite decimal system": [
            "4",
            "5.0",
            "5.1",
            "5.2",
            "5.3",
            "5.4",
            "5.5",
            "5.6",
            "5.7",
            "5.8",
            "5.9",
            "5.10a",
            "5.10b",
            "5.10c",
            "5.10d",
            "5.11a",
            "5.11b",
            "5.11c",
            "5.11d",
            "5.12a",
            "5.12b",
            "5.12c",
            "5.12d",
            "5.13a",
            "5.13b",
            "5.13c",
            "5.13d",
            "5.14a",
            "5.14b",
            "5.14c",
            "5.14d",
            "5.15a",
            "5.15b",
            "5.15c",
            "5.15d",
            "5.16a",
            "5.16b",
            "5.16c",
            "5.16d",
        ]
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
