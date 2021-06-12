from fastapi import APIRouter

from app import create_api, VoteDefinition


router = APIRouter(
    tags=["climbs"],
)


create_api(
    router,
    model_name="Climbs",
    collection_name="climbs",
    item_name="climb",
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
        ),
        VoteDefinition(
            model_name="GradeVote",
            collection_name="grade_votes",
            item_name="grade_vote",
            type=str,  # TODO system + grade
        ),
        VoteDefinition(
            model_name="ClimbTypeVote",
            collection_name="climb_type_votes",
            item_name="climb_type_vote",
            type=str,  # TODO enum: sport, boulder, partially bolted, trad, alpine
        ),
        # guide book grade?
        # first ascent grade?
    ]
)
