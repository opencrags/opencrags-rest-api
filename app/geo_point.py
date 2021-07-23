from pydantic import BaseModel
from typing import Tuple, Literal


class GeoPoint(BaseModel):
    type: Literal["Point"]
    coordinates: Tuple[float, float]
