from PIL import Image
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional


class ImageId(BaseModel):
    image_id: UUID = Field(..., alias="id")


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


class IdentifiedImage(Image, ImageId):
    pass
