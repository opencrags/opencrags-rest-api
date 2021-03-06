from uuid import UUID

from app import GeoPoint, create_api_router, VoteDefinition


router, MainModel, vote_models = create_api_router(
    model_name="Parking",
    collection_name="parkings",
    item_name="parking",
    statics=dict(
        crag_id=UUID,
    ),
    voted=[
        VoteDefinition(
            model_name="ParkingCoordinateVote",
            collection_name="coordinate_votes",
            item_name="coordinate_vote",
            type=GeoPoint,
        ),
    ]
)
