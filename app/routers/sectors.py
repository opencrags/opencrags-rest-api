from uuid import UUID
from typing import List

from app import GeoPoint, create_api_router, VoteDefinition


# TODO: area vote?

router, MainModel, vote_models = create_api_router(
    model_name="Sector",
    collection_name="sectors",
    item_name="sector",
    statics=dict(
        crag_id=UUID
    ),
    voted=[
        VoteDefinition(
            model_name="SectorNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="GuideImagesVote",
            collection_name="guide_images_votes",
            item_name="guide_images_vote",
            type=List[UUID],
        ),
        VoteDefinition(
            model_name="CoordinateVote",
            collection_name="coordinate_votes",
            item_name="coordinate_vote",
            type=GeoPoint,
        ),
        VoteDefinition(
            model_name="SectorThumbnailVote",
            collection_name="sector_thumbnail_votes",
            item_name="sector_thumbnail_vote",
            type=UUID,
        ),
    ],
)
