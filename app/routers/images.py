from uuid import UUID
from fastapi import APIRouter

from app import create_api, VoteDefinition


router = APIRouter(
    tags=["images"],
)


create_api(
    router,
    model_name="Image",
    collection_name="images",
    item_name="image",
    statics=dict(
        sector_id=UUID,
        base64_image=str,
    ),
)
