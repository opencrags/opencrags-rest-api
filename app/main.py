from fastapi import FastAPI, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
import random
import io
from uuid import UUID
import base64
import json
from pathlib import Path
import PIL
from pydantic import BaseModel, validator, Field
from typing import List, Union, Literal, Optional


app = FastAPI(
    title="opencrags-rest-api",
    description="Database of lead climbs and boulder problems",
    version="0.0.0",
)


@app.get("/", status_code=status.HTTP_303_SEE_OTHER, include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


class Image(BaseModel):
    base64_image: Optional[str] = Field(..., example="/9j/4AAQSkZJRgAB...")

    def image(self):
        return PIL.Image.open(
            io.BytesIO(
                base64.b64decode(self.base64_image)
            )
        )

class Climb(Image):
    climb_id: UUID = Field(..., alias="id")

@app.post(
    "/climbs",
    response_model=Climb,
    status_code=status.HTTP_201_CREATED,
)
def add_climb(
    image: Image,
):
    climb_id = UUID(int=random.getrandbits(128))
    return Climb(id=climb_id)


@app.delete(
    "/climbs/{climb_id}",
    status_code=status.HTTP_200_OK,
)
def remove_climb(
    climb_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@app.get(
    "/climbs/{climb_id}",
    response_model=Climb,
    status_code=status.HTTP_200_OK,
)
def view_climb(
    climb_id: UUID,
):
    climb_id = UUID(int=random.getrandbits(128))
    return Climb(id=climb_id)


class CragInfo(BaseModel):
    name: str

class Crag(CragInfo):
    crag_id: UUID = Field(..., alias="id")

@app.post(
    "/crags/{crag_id}",
    response_model=Crag,
    status_code=status.HTTP_201_CREATED,
)
def add_crag(crag_info: CragInfo):
    crag_id = UUID(int=random.getrandbits(128))
    return Crag(
        id=crag_id,
        name=crag_info.name,
    )


@app.delete(
    "/crags/{crag_id}",
    status_code=status.HTTP_200_OK,
)
def remove_crag(
    crag_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@app.get(
    "/crags",
    response_model=List[Crag],
    status_code=status.HTTP_200_OK,
)
def list_crags():
    pass


@app.post(
    "/quickSearch",
    response_model=List[Union[Climb, Crag]],
    status_code=status.HTTP_200_OK,
)
def search_crags_and_climbs(
    text: str,
    limit: int = 16,
):
    query_encoding = text_or_image.encoding()

    return [
        RankedImageItem(id=rank.item_id, rank=rank.rank)
        for rank in indexes[collection_id].rank(query_encoding, limit)
    ]


@app.post(
    "/climbs/search",
    response_model=List[Climb],
    status_code=status.HTTP_200_OK,
)
def advanced_search_for_climbs(
    type: str,
    grade: str,
    stars: str,
    ascents: str,
    distance: str,
    start: int = 0,
    stop: int = 20,
):
    pass
