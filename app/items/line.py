from uuid import UUID
from pydantic import BaseModel, Field


class LineId(BaseModel):
    line_id: UUID = Field(..., alias="id")


class Line(BaseModel):
    climb_id: UUID
    image_id: UUID
    line_path: str # list of coordinates?


class IdentifiedLine(LineId, Line):
    pass
