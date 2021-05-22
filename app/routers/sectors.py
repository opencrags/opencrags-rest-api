from fastapi import APIRouter, Response, status, HTTPException, Query
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

from app.items.crag import Crag
from app.items.sector import Sector, SectorId, IdentifiedSector


router = APIRouter(
    tags=["sectors"],
)


@router.post(
    "/crags/{crag_id}/sectors",
    response_model=Sector,
    status_code=status.HTTP_201_CREATED,
)
def add_sector_to_crag(crag_id: UUID, sector: Sector):
    sector_id = UUID(int=random.getrandbits(128))
    return SectorId(id=sector_id)


@router.put(
    "/crags/{crag_id}/sectors/{sector_id}",
    response_model=Crag,
    status_code=status.HTTP_201_CREATED,
)
def update_sector(crag_id: UUID, sector_id: UUID, sector: Sector):
    return SectorId(id=sector_id)


@router.delete(
    "/crags/{crag_id}/sectors/{sector_id}",
    status_code=status.HTTP_200_OK,
)
def remove_sector_from_crag(
    crag_id: UUID,
    sector_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/crags/{crag_id}/sectors/{sector_id}",
    response_model=List[IdentifiedSector],
    status_code=status.HTTP_200_OK,
)
def view_sector(
    crag_id: UUID,
    sector_id: UUID,
):
    pass

