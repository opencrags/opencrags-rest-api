from pydantic import BaseModel, Field

from app import mongo


class CragId(BaseModel):
    crag_id: mongo.ObjectId = Field(..., alias="id")


class Crag(BaseModel):
    name: str
    # location_polygon: str  # calculated


class IdentifiedCrag(CragId, Crag):
    pass
