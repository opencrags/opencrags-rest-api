from enum import Enum
from uuid import UUID

from app import create_api_router, VoteDefinition, VoteAggregation


def most_voted(mongo_votes):
    values = dict()
    for mongo_vote in mongo_votes:
        if mongo_vote["value"] in values:
            values[mongo_vote["value"]] += 1
        else:
            values[mongo_vote["value"]] = 1
    return max(values, key=values.get, default=None)


def average(mongo_votes):
    if len(mongo_votes) == 0:
        return None
    else:
        return sum([mongo_vote["value"] for mongo_vote in mongo_votes]) / len(mongo_votes)


class ClimbType(str, Enum):
    boulder = "boulder"
    sport = "sport"
    deep_water_solo = "deep_water_solo"
    traditional = "traditional"
    partially_bolted = "partially_bolted"
    ice_or_mixed = "ice_or_mixed"
    aid = "aid"
    mountain = "mountain"


router, MainModel, vote_models = create_api_router(
    model_name="Climbs",
    collection_name="climbs",
    item_name="climb",
    statics=dict(
        crag_id=UUID,
        sector_id=UUID,
    ),
    voted=[
        VoteDefinition(
            model_name="ClimbNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="RatingVote",
            collection_name="rating_votes",
            item_name="rating_vote",
            type=int,
            aggregation=VoteAggregation(
                fn=average,
                name="average_rating",
                type=float,
            ),
        ),
        VoteDefinition(
            model_name="GradeVote",
            collection_name="grade_votes",
            item_name="grade_vote",
            type=UUID,
            aggregation=VoteAggregation(
                fn=most_voted,
                name="most_voted_grade",
                type=UUID,
            ),
        ),
        VoteDefinition(
            model_name="ClimbTypeVote",
            collection_name="climb_type_votes",
            item_name="climb_type_vote",
            type=ClimbType,
        ),
        VoteDefinition(
            model_name="SitStartVote",
            collection_name="sit_start_votes",
            item_name="sit_start_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="DefinedStartVote",
            collection_name="defined_start_votes",
            item_name="defined_start_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="EliminationsVote",
            collection_name="eliminations_votes",
            item_name="eliminations_vote",
            type=str,  # TODO: draw area of eliminations?
        ),
        VoteDefinition(
            model_name="DescriptionVote",
            collection_name="description_votes",
            item_name="description_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="BrokenVote",
            collection_name="broken_votes",
            item_name="broken_vote",
            type=bool,
        ),
        VoteDefinition(
            model_name="BetaVideoVote",
            collection_name="beta_video_votes",
            item_name="beta_video_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="ExternalLinkVote",
            collection_name="external_link_votes",
            item_name="external_link_vote",
            type=str,
        ),
        # guide book grade?
        # first ascent grade?
        # point to other page with information?
        # point to video + timestamp with beta
    ]
)
