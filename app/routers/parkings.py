from fastapi import APIRouter

from app import create_api_router, VoteDefinition


router = create_api_router(
    model_name="Parking",
    collection_name="parkings",
    item_name="parking",
    voted=[
        VoteDefinition(
            model_name="ParkingCoordinateVote",
            collection_name="coordinate_votes",
            item_name="coordinate_vote",
            type=str,
        ),
    ]
)
