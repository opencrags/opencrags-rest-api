from uuid import UUID
from typing import Literal
from pydantic.types import constr
from typing import Optional

from app import create_api_router, VoteDefinition


router, MainModel, vote_models = create_api_router(
    model_name="BetaVideos",
    collection_name="beta_videos",
    item_name="beta_video",
    statics=dict(
        climb_id=UUID,
        video_url=constr(min_length=1, strip_whitespace=True),
        timestamp=Optional[constr(min_length=1, strip_whitespace=True)],
    ),
    voted=[
        VoteDefinition(
            model_name="LikeBetaVideoVote",
            collection_name="like_votes",
            item_name="like_vote",
            type=Literal[True],
        ),
    ],
)
