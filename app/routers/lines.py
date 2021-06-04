from uuid import UUID
from fastapi import APIRouter

from app import create_api, VoteDefinition


router = APIRouter(
    tags=["lines"],
)


# TODO: only allow one line per image + climb

create_api(
    router,
    model_name="Line",
    collection_name="lines",
    item_name="line",
    statics=dict(
        climb=UUID,
        image=UUID,
    ),
    voted=[
        VoteDefinition(
            model_name="ClimbVote",
            collection_name="climb_votes",
            item_name="climb_vote",
            type=UUID,
        ),
        VoteDefinition(
            model_name="LinePathVote",
            collection_name="line_path_votes",
            item_name="line_path_vote",
            type=str,
        ),
    ]
)
