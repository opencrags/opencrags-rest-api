from uuid import UUID
from datetime import date
from fastapi import APIRouter

from app import create_api, VoteDefinition


router = APIRouter(
    tags=["ascents"],
)


create_api(
    router,
    model_name="Ascent",
    collection_name="ascents",
    item_name="ascent",
    statics=dict(
        climb_id=UUID,
        ascent_date=date,
    ),
)
