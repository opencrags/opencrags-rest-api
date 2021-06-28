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


router = APIRouter(
    tags=["utilities"],
)


@router.get(
    "/quick-search",
    # response_model=List[Union[Crag, IdentifiedClimb]],
    status_code=status.HTTP_200_OK,
)
def search_crags_sectors_and_climbs_by_name(
    text: str,
    limit: int = 16,
):
    pass
