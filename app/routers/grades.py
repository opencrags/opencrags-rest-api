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
    fuzzy_unified_rank: float


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
    if system is not None:
        filters["systen"] = system
    if grade is not None:
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
    # https://www.thecrag.com/en/article/grades
    system_grades = {
        "Fontainebleau grading system": [
            ("1", 1),
            ("2", 2),
            ("3", 3),
            ("4", 4),
            ("4+", 5),
            ("5", 6),
            ("5+", 7),
            ("6A", 8),
            ("6A+", 9),
            ("6B", 10),
            ("6B+", 11),
            ("6C", 12),
            ("6C+", 13),
            ("7A", 14),
            ("7A+", 15),
            ("7B", 16),
            ("7B+", 17),
            ("7C", 18),
            ("7C+", 19),
            ("8A", 20),
            ("8A+", 21),
            ("8B", 22),
            ("8B+", 23),
            ("8C", 24),
            ("8C+", 25),
            ("9A", 26),
            ("9A+", 27),
            ("9B", 28),
            ("9B+", 29),
            ("9C", 30),
            ("9C+", 31),
        ],
        # https://en.wikipedia.org/wiki/Grade_(bouldering)
        "Hueco scale": [
            ("VB", 2),
            ("V0", 4),
            ("V0+", 5),
            ("V1", 6),
            ("V2", 7.5),
            ("V3", 9),
            ("V4", 10.5),
            ("V5", 12.25),
            ("V6", 13.5),
            ("V7", 14.5),
            ("V8", 16.5),
            ("V9", 17.5),
            ("V10", 18.75),
            ("V11", 20),
            ("V12", 21),
            ("V13", 22),
            ("V14", 23),
            ("V15", 24),
            ("V16", 25),
            ("V17", 26),
            ("V18", 27),
            ("V19", 28),
            ("V20", 29),
        ],
        # https://www.mec.ca/en/explore/climbing-grade-conversion
        "French numerical system": [
            ("1", 0.5),
            ("2", 1),
            ("3", 1.5),
            ("4a", 2),
            ("4b", 2.5),
            ("4c", 3),
            ("5a", 3.5),
            ("5b", 4),
            ("5c", 5),
            ("6a", 6),
            ("6a+", 6.5),
            ("6b", 7),
            ("6b+", 7.5),
            ("6c", 8),
            ("6c+", 9),
            ("7a", 10),
            ("7a+", 11),
            ("7b", 12),
            ("7b+", 13),
            ("7c", 14),
            ("7c+", 15),
            ("8a", 16),
            ("8a+", 17),
            ("8b", 18),
            ("8b+", 19),
            ("8c", 20),
            ("8c+", 21),
            ("9a", 22),
            ("9a+", 23),
            ("9b", 24),
            ("9b+", 25),
            ("9c", 26),
            ("9c+", 27),
        ],
        # https://en.wikipedia.org/wiki/Grade_(climbing)
        "Yosemite decimal system": [
            ("4", 0.5),
            ("5.0", 0.75),
            ("5.1", 1),
            ("5.2", 1.25),
            ("5.3", 1.5),
            ("5.4", 2),
            ("5.5", 2.5),
            ("5.6", 3),
            ("5.7", 3.5),
            ("5.8", 4),
            ("5.9", 5),
            ("5.10a", 6),
            ("5.10b", 6.5),
            ("5.10c", 7),
            ("5.10d", 7.5),
            ("5.11a", 8),
            ("5.11b", 8.5),
            ("5.11c", 9),
            ("5.11d", 10),
            ("5.12a", 11),
            ("5.12b", 12),
            ("5.12c", 13),
            ("5.12d", 14),
            ("5.13a", 15),
            ("5.13b", 16),
            ("5.13c", 17),
            ("5.13d", 18),
            ("5.14a", 19),
            ("5.14b", 20),
            ("5.14c", 21),
            ("5.14d", 22),
            ("5.15a", 23),
            ("5.15b", 24),
            ("5.15c", 25),
            ("5.15d", 26),
            ("5.16a", 27),
            ("5.16b", 28),
            ("5.16c", 29),
            ("5.16d", 30),
        ]
    }

    for system, grades in system_grades.items():
        for index, (grade, fuzzy_unified_rank) in enumerate(grades):
            mongo.db.grade_system_grades.insert_one(GradeSystemGrade(
                id=uuid4(),
                system=system,
                grade=grade,
                rank=index,
                fuzzy_unified_rank=fuzzy_unified_rank,
            ).dict())

if mongo.db.grade_system_grades.count_documents({}) == 0:
    add_grades()
