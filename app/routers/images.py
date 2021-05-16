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

from app.items.image import Image, ImageId, ImageInfo, IdentifiedImage


router = APIRouter(
    tags=["images"],
)


@router.post(
    "/images",
    response_model=ImageId,
    status_code=status.HTTP_201_CREATED,
)
def add_image(
    image: Image,
):
    image_id = UUID(int=random.getrandbits(128))
    return ImageId(id=image_id)


@router.put(
    "/images/{image_id}",
    status_code=status.HTTP_200_OK,
)
def update_image_info(
    image_id: UUID,
    image_info: ImageInfo,
):
    pass


@router.delete(
    "/images/{image_id}",
    status_code=status.HTTP_200_OK,
)
def remove_image(
    image_id: UUID,
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/images/{image_id}",
    response_model=IdentifiedImage,
    status_code=status.HTTP_200_OK,
)
def view_image(
    image_id: UUID,
):
    pass


@router.get(
    "/images",
    response_model=List[IdentifiedImage],
    status_code=status.HTTP_200_OK,
)
def list_images_for_a_climb(
    climd_id: UUID,
):
    pass
