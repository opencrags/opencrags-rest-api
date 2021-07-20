from uuid import UUID
from fastapi import APIRouter

from app import create_api_router, VoteDefinition


# TODO: only allow one line per image + climb
# TODO: check that image + climb belong to the sector

router = create_api_router(
    model_name="Line",
    collection_name="lines",
    item_name="line",
    statics=dict(
        sector_id=UUID,
        climb_id=UUID,
        image_id=UUID,
    ),
    voted=[
        VoteDefinition(
            model_name="LinePathVote",
            collection_name="line_path_votes",
            item_name="line_path_vote",
            type=str,
        ),
    ]
)
