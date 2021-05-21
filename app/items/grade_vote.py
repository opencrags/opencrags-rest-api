from uuid import UUID
from pydantic import BaseModel, Field

from app.items.grade import Grade


class GradeVoteId(BaseModel):
    grade_vote_id: UUID = Field(..., alias="id")


class GradeVote(BaseModel):
    user_id: UUID
    climb_id: UUID
    grade: Grade


class IdentifiedGradeVote(GradeVoteId, GradeVote):
    pass
