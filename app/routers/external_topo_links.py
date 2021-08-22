from uuid import UUID
from typing import Literal
from pydantic.types import constr
from typing import Optional

from app import create_api_router, VoteDefinition


router, MainModel, vote_models = create_api_router(
    model_name="ExernalTopoLinks",
    collection_name="external_topo_links",
    item_name="external_topo_link",
    statics=dict(
        climb_id=UUID,
        external_url=constr(min_length=1, strip_whitespace=True),
    ),
    voted=[
        VoteDefinition(
            model_name="LikeExternalTopoLinkVote",
            collection_name="like_votes",
            item_name="like_vote",
            type=Literal[True],
        ),
    ],
)
