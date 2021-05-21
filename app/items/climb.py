from uuid import UUID
from pydantic import BaseModel, Field

from app.items.grade import Grade


class ClimbId(BaseModel):
    climb_id: UUID = Field(..., alias="id")


class Climb(BaseModel):
    name: str
    type: str # sport, boulder, partially bolted, trad, alpine
    sector_id: UUID
    first_ascent_grade: Grade
    # tags?


class IdentifiedClimb(ClimbId, Climb):
    pass
