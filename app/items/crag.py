from pydantic import BaseModel, Field

from app import mongo


class Crag(mongo.Model):
    name: str
    # location_polygon: str  # calculated
