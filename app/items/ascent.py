from uuid import UUID
from pydantic import BaseModel, Field


class AscentId(BaseModel):
    climb_id: UUID = Field(..., alias="id")


class Ascent(BaseModel):
    user_id: UUID
    climb_id: UUID


class IdentifiedAscent(AscentId, Ascent):
    pass
