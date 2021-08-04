from uuid import UUID

from app import create_api_router


# TODO: downsize image height
# TODO: maxsize limit
# TODO: only allow jpeg

router, MainModel, vote_models = create_api_router(
    model_name="Banner",
    collection_name="banners",
    item_name="banner",
    statics=dict(
        crag_id=UUID,
        base64_image=str,
    ),
)
