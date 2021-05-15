from uuid import UUID
from pydantic import BaseModel, Field


class ClimbId(BaseModel):
    climb_id: UUID = Field(..., alias="id")


class Climb(BaseModel):
    name: str
    sector_id: UUID


class IdentifiedClimb(ClimbId, Climb):
    pass
