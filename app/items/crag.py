from uuid import UUID
from pydantic import BaseModel, Field


class CragId(BaseModel):
    crag_id: UUID = Field(..., alias="id")


class Crag(BaseModel):
    name: str
    location_polygon: str


class IdentifiedCrag(CragId, Crag):
    pass
