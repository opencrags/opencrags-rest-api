from uuid import UUID
from pydantic import BaseModel, Field


class GradeVoteId(BaseModel):
    crag_id: UUID = Field(..., alias="id")


class GradeVote(BaseModel):
    name: str
    location_polygon: str


class IdentifiedGradeVote(GradeVoteId, GradeVote):
    pass
