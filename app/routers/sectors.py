from fastapi import APIRouter

from app import create_api, Voted


router = APIRouter(
    tags=["sectors"],
)


create_api(
    router,
    model_name="Sector",
    collection_name="sectors",
    item_name="sector",
    voted=[
        Voted(
            model_name="SectorNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        ),
    ]
)
