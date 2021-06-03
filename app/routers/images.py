from fastapi import APIRouter

from app import create_api, Voted


router = APIRouter(
    tags=["images"],
)


# TODO: requires static content that is not voted on?

create_api(
    router,
    model_name="Image",
    collection_name="images",
    item_name="image",
    voted=[
        Voted(
            model_name="ImageQualityVote",
            collection_name="quality_votes",
            item_name="quality_vote",
            type=int,
        ),
    ]
)
