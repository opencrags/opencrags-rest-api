from uuid import UUID
import pymongo
from pydantic import BaseModel
from typing import List

from app import create_api_router, VoteDefinition, mongo


# TODO: check that image + climb belong to the same sector

class LineNode(BaseModel):
    x: float
    y: float


router, MainModel, vote_models = create_api_router(
    model_name="Line",
    collection_name="lines",
    item_name="line",
    statics=dict(
        climb_id=UUID,
        image_id=UUID,
        sector_id=UUID,
    ),
    voted=[
        VoteDefinition(
            model_name="LinePathVote",
            collection_name="line_path_votes",
            item_name="line_path_vote",
            type=List[LineNode],
        ),
    ]
)

mongo.db.lines.create_index([
    ("climb_id", pymongo.ASCENDING),
    ("image_id", pymongo.ASCENDING),
], unique=True)
