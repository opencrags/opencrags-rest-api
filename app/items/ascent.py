from uuid import UUID
import datetime
from pydantic import BaseModel, Field, conint


class AscentId(BaseModel):
    climb_id: UUID = Field(..., alias="id")


class Ascent(BaseModel):
    user_id: UUID
    climb_id: UUID
    date: datetime.date
    flash: bool = False
    first_ascent: bool = False
    attempts: Optional[conint(ge=1)]


class IdentifiedAscent(AscentId, Ascent):
    pass
