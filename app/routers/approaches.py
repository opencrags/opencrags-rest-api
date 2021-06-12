from fastapi import APIRouter

from app import create_api_router, VoteDefinition


router = create_api_router(
    model_name="Approach",
    collection_name="approaches",
    item_name="approach",
    voted=[
        VoteDefinition(
            model_name="ApproachPathVote",
            collection_name="path_votes",
            item_name="path_vote",
            type=str,
        ),
    ]
)
