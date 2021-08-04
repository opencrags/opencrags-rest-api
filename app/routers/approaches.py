from uuid import UUID
from pydantic import BaseModel
from typing import List, Tuple, Literal

from app import create_api_router, VoteDefinition


class GeoLine(BaseModel):
    type: Literal["LineString"]
    coordinates: List[Tuple[float, float]]


router, MainModel, vote_models = create_api_router(
    model_name="Approach",
    collection_name="approaches",
    item_name="approach",
    statics=dict(
        crag_id=UUID,
    ),
    voted=[
        VoteDefinition(
            model_name="ApproachPathVote",
            collection_name="path_votes",
            item_name="path_vote",
            type=GeoLine,
        ),
    ]
)
