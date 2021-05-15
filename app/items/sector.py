from uuid import UUID
from pydantic import BaseModel, Field


class Sector(BaseModel):
    name: str
    crag_id: UUID


class SectorId(BaseModel):
    sector_id: UUID = Field(..., alias="id")


class IdentifiedSector(SectorId, Sector):
    pass
