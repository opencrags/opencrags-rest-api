from fastapi import APIRouter

from app import create_api, Voted


router = APIRouter(
    tags=["ascents"],
)


create_api(
    router,
    model_name="Ascent",
    collection_name="ascents",
    item_name="ascent",
    voted=[
        Voted(
            model_name="AscentNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        )
    ]
)
