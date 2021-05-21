from uuid import UUID
from pydantic import BaseModel, Field


class LineId(BaseModel):
    crag_id: UUID = Field(..., alias="id")


class Line(BaseModel):
    climb_id: UUID
    image_id: UUID
    name: str
    line_path: str


class IdentifiedLine(LineId, Line):
    pass
