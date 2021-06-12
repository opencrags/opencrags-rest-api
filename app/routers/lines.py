from uuid import UUID
from fastapi import APIRouter

from app import create_api_router, VoteDefinition


# TODO: only allow one line per image + climb

router = create_api_router(
    model_name="Line",
    collection_name="lines",
    item_name="line",
    statics=dict(
        climb=UUID,
        image=UUID,
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
