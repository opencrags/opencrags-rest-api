from fastapi import APIRouter, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
import random
import io
from uuid import UUID
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Union, Literal, Optional

from app.items.grade_vote import GradeVote, GradeVoteId, IdentifiedGradeVote


router = APIRouter(
    tags=["grade_votes"],
)


@router.post(
    "/gradeVotes",
    response_model=GradeVoteId,
    status_code=status.HTTP_201_CREATED,
)
def add_grade_vote(
    climb_id: UUID,
    grade_vote: GradeVote,
):
    grade_vote_id = UUID(int=random.getrandbits(128))
    return GradeVoteId(id=grade_vote_id)



@router.put(
    "/gradeVotes/{grade_vote_id}",
    response_model=IdentifiedGradeVote,
    status_code=status.HTTP_200_OK,
)
def update_grade_vote(
    climb_id: UUID,
    grade_vote_id: UUID,
    grade_vote: GradeVote,
):
    pass


@router.delete(
    "/gradeVotes/{grade_vote_id}",
    status_code=status.HTTP_200_OK,
)
def remove_vote(
    climb_id: UUID,
    grade_vote_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/gradeVotes/{grade_vote_id}",
    response_model=IdentifiedGradeVote,
    status_code=status.HTTP_200_OK,
)
def view_vote(
    climb_id: UUID,
    grade_vote_id: UUID,
):
    pass


@router.get(
    "/gradeVotes",
    response_model=List[IdentifiedGradeVote],
    status_code=status.HTTP_200_OK,
)
def list_public_grade_votes(
    climd_id: UUID,
):
    pass


@router.get(
    "/gradeVotes/summary",
    # response_model=List[IdentifiedGradeVote],
    status_code=status.HTTP_200_OK,
    description="Includes private votes",
)
def summary_of_private_and_public_grade_votes(
    climd_id: UUID,
):
    pass
