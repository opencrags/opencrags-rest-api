from uuid import UUID
from pydantic import BaseModel, Field


class ClimbId(BaseModel):
    climb_id: UUID = Field(..., alias="id")


class Climb(BaseModel):
    name: str
    type: str # sport, boulder, partially bolted, trad, alpine
    sector_id: UUID
    first_ascent_grade: str
    # tags?


class Grade(BaseModel):
    system: str
    grade: str


class IdentifiedClimb(ClimbId, Climb):
    pass
