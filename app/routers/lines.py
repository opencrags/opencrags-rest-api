from uuid import UUID
from fastapi import APIRouter

from app import create_api, Voted


router = APIRouter(
    tags=["lines"],
)


create_api(
    router,
    model_name="Line",
    collection_name="lines",
    item_name="line",
    voted=[
        Voted(
            model_name="ClimbVote",
            collection_name="climb_votes",
            item_name="climb_vote",
            type=UUID,
        ),
        Voted(
            model_name="LineQualityVote",
            collection_name="quality_votes",
            item_name="quality_vote",
            type=int,
        ),
    ]
)
