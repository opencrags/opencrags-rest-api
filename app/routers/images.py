from uuid import UUID
from fastapi import APIRouter

from app import create_api_router, VoteDefinition


# TODO: downsize image height
# TODO: maxsize limit
# TODO: only allow jpeg

router = create_api_router(
    model_name="Image",
    collection_name="images",
    item_name="image",
    statics=dict(
        sector_id=UUID,
        base64_image=str,
    ),
)

# TODO: Custom api? uri: /static/images/{image_id}.png
# {
#     image_uri: f"http://opencrags.com/static/images/{image_id}.png"
# }
