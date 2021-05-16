from uuid import UUID
from pydantic import BaseModel, Field


class RatingId(BaseModel):
    climb_id: UUID = Field(..., alias="id")


class Rating(BaseModel):
    stars: int


class IdentifiedRating(RatingId, Rating):
    pass
