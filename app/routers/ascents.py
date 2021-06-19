from typing import Optional
from uuid import UUID
from datetime import date
from pydantic import conint
from fastapi import APIRouter

from app import create_api_router, VoteDefinition


router = create_api_router(
    model_name="Ascent",
    collection_name="ascents",
    item_name="ascent",
    statics=dict(
        climb_id=UUID,
        ascent_date=date,
        flash=bool,
        attempts=Optional[conint(ge=1)],
        public=bool, # TODO: does this need to be a custom api?
    ),
)
