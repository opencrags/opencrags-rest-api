from uuid import UUID
from enum import Enum

from app import create_api_router, VoteDefinition


class GradeSystem(str, Enum):
    FONT = "Fontainebleau grading system"
    HUECO = "Hueco scale"
    FRENCH = "French numerical system"
    YDS = "Yosemite decimal system"


router = create_api_router(
    model_name="Crag",
    collection_name="crags",
    item_name="crag",
    statics=dict(
        grade_system=GradeSystem,
    ),
    voted=[
        VoteDefinition(
            model_name="CragNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="CragBannerVote",
            collection_name="banner_votes",
            item_name="banner_vote",
            type=UUID,
        ),
    ]
)
