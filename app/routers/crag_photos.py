from uuid import UUID
from typing import Literal

from app import create_api_router, VoteDefinition


# TODO: downsize image height
# TODO: maxsize limit
# TODO: only allow jpeg

router, MainModel, vote_models = create_api_router(
    model_name="CragPhotos",
    collection_name="crag_photos",
    item_name="crag_photo",
    statics=dict(
        crag_id=UUID,
        base64_image=str,
    ),
    voted=[
        VoteDefinition(
            model_name="LikeVote",
            collection_name="like_votes",
            item_name="like_vote",
            type=Literal[True],
        ),
    ],
)
