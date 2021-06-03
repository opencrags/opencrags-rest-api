from fastapi import APIRouter

from app import create_api, Voted


router = APIRouter(
    tags=["climbs"],
)


create_api(
    router,
    model_name="Climbs",
    collection_name="climbs",
    item_name="climb",
    voted=[
        Voted(
            model_name="ClimbNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        ),
        Voted(
            model_name="RatingVote",
            collection_name="rating_votes",
            item_name="rating_vote",
            type=int,
        ),
        Voted(
            model_name="GradeVote",
            collection_name="grade_votes",
            item_name="grade_vote",
            type=str,  # TODO
        ),
    ]
)
