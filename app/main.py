from fastapi import FastAPI, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
import random
import io
from uuid import UUID
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Union, Literal, Optional


app = FastAPI(
    title="opencrags-rest-api",
    description="Database of boulder problems and routes",
    version="0.0.0",
)


@app.get("/", status_code=status.HTTP_303_SEE_OTHER, include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


class Crag(BaseModel):
    name: str
    location_polygon: str

class CragId(BaseModel):
    crag_id: UUID = Field(..., alias="id")

@app.post(
    "/crags",
    response_model=CragId,
    status_code=status.HTTP_201_CREATED,
    tags=["crags"],
)
def add_crag(crag: Crag):
    crag_id = UUID(int=random.getrandbits(128))
    return CragId(id=crag_id)


@app.put(
    "/crags/{crag_id}",
    response_model=Crag,
    status_code=status.HTTP_200_OK,
    tags=["crags"],
)
def update_crag(crag_id: UUID, crag: Crag):
    crag_id = UUID(int=random.getrandbits(128))
    return CragId(id=crag_id)


@app.delete(
    "/crags/{crag_id}",
    status_code=status.HTTP_200_OK,
    tags=["crags"],
)
def remove_crag(
    crag_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)



class IdentifiedCrag(CragId, Crag):
    pass

@app.get(
    "/crags/{crag_id}",
    response_model=IdentifiedCrag,
    status_code=status.HTTP_200_OK,
    tags=["crags"],
)
def view_crag():
    pass


class Sector(BaseModel):
    name: str
    crag_id: UUID

class SectorId(BaseModel):
    sector_id: UUID = Field(..., alias="id")

@app.post(
    "/crags/{crag_id}/sectors",
    response_model=Crag,
    status_code=status.HTTP_201_CREATED,
    tags=["crags/sectors"],
)
def add_sector_to_crag(crag_id: UUID, sector: Sector):
    sector_id = UUID(int=random.getrandbits(128))
    return SectorId(id=sector_id)


@app.put(
    "/crags/{crag_id}/sectors/{sector_id}",
    response_model=Crag,
    status_code=status.HTTP_201_CREATED,
    tags=["crags/sectors"],
)
def update_sector(crag_id: UUID, sector_id: UUID, sector: Sector):
    return SectorId(id=sector_id)


@app.delete(
    "/crags/{crag_id}/sectors/{sector_id}",
    status_code=status.HTTP_200_OK,
    tags=["crags/sectors"],
)
def remove_sector_from_crag(
    crag_id: UUID,
    sector_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


class IdentifiedSector(SectorId, Sector):
    pass

@app.get(
    "/crags/{crag_id}/sectors/{sector_id}",
    response_model=List[IdentifiedSector],
    status_code=status.HTTP_200_OK,
    tags=["crags/sectors"],
)
def view_sector(
    crag_id: UUID,
    sector_id: UUID,
):
    pass


class ImageInfo(BaseModel):
    location: str
    sector_id: Optional[UUID]

class Image(ImageInfo):
    base64_image: str = Field(..., example="/9j/4AAQSkZJRgAB...")

    def image(self):
        return PIL.Image.open(
            io.BytesIO(
                base64.b64decode(self.base64_image)
            )
        )

class ImageId(BaseModel):
    image_id: UUID = Field(..., alias="id")

@app.post(
    "/images",
    response_model=ImageId,
    status_code=status.HTTP_201_CREATED,
    tags=["images"],
)
def add_image(
    image: Image,
):
    image_id = UUID(int=random.getrandbits(128))
    return ImageId(id=image_id)


@app.put(
    "/images/{image_id}",
    status_code=status.HTTP_200_OK,
    tags=["images"],
)
def update_image_info(
    image_id: UUID,
    image_info: ImageInfo,
):
    pass


@app.delete(
    "/images/{image_id}",
    status_code=status.HTTP_200_OK,
    tags=["images"],
)
def remove_image(
    image_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


class IdentifiedImage(Image, ImageId):
    pass

@app.get(
    "/images/{image_id}",
    response_model=IdentifiedImage,
    status_code=status.HTTP_200_OK,
    tags=["images"],
)
def view_image(
    image_id: UUID,
):
    pass


class Climb(BaseModel):
    name: str
    sector_id: UUID

class ClimbId(BaseModel):
    climb_id: UUID = Field(..., alias="id")

@app.post(
    "/climbs",
    response_model=Climb,
    status_code=status.HTTP_201_CREATED,
    tags=["climbs"],
)
def add_climb(
    climb: Climb,
):
    climb_id = UUID(int=random.getrandbits(128))
    return ClimbId(id=climb_id)


class IdentifiedClimb(ClimbId, Climb):
    pass

@app.put(
    "/climbs/{climb_id}",
    response_model=IdentifiedClimb,
    status_code=status.HTTP_200_OK,
    tags=["climbs"],
)
def update_climb(
    climb_id: UUID,
    climb: Climb,
):
    pass


@app.delete(
    "/climbs/{climb_id}",
    status_code=status.HTTP_200_OK,
    tags=["climbs"],
)
def remove_climb(
    climb_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@app.get(
    "/climbs/{climb_id}",
    response_model=IdentifiedClimb,
    status_code=status.HTTP_200_OK,
    tags=["climbs"],
)
def view_climb(
    climb_id: UUID,
):
    pass


class ClimbType(str, Enum):
    any = "any"
    boulder = "boulder"
    route = "route"

class SortBy(str, Enum):
    distance = "distance"
    grade = "grade"
    stars = "stars"
    ascents = "ascents"

class SortOrder(str, Enum):
    ascending = "ascending"
    descending = "descending"

@app.get(
    "/climbs",
    response_model=List[Climb],
    status_code=status.HTTP_200_OK,
    tags=["climbs"],
)
def advanced_search_for_climbs(
    type: ClimbType,
    min_grade: str = "4",
    max_grade: str = "9C",
    min_stars: float = Query(0, ge=0),
    max_stars: float = Query(5, ge=0),
    min_ascents: int = Query(0, ge=0),
    max_ascents: int = Query(999999, ge=0),
    location: str = Query(...),
    min_distance: float = Query(0, ge=0),
    max_distance: float = Query(100, ge=0),
    sort_by: SortBy = Query(SortBy.distance),
    sort_order: SortOrder = Query(SortOrder.ascending),
    start: int = 0,
    limit: int = Query(20, le=100),
):
    pass


@app.get(
    "/quickSearch",
    response_model=List[Union[Climb, Crag]],
    status_code=status.HTTP_200_OK,
)
def search_crags_sectors_and_climbs_by_name(
    text: str,
    limit: int = 16,
):
    query_encoding = text_or_image.encoding()

    return [
        RankedImageItem(id=rank.item_id, rank=rank.rank)
        for rank in indexes[collection_id].rank(query_encoding, limit)
    ]
