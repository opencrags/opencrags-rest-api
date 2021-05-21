from uuid import UUID
from pydantic import BaseModel, Field


class RatingId(BaseModel):
    rating_id: UUID = Field(..., alias="id")


class Rating(BaseModel):
    stars: int


class IdentifiedRating(RatingId, Rating):
    pass
