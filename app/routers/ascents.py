from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import conint

from app import create_api_router


router, MainModel, vote_models = create_api_router(
    model_name="Ascent",
    collection_name="ascents",
    item_name="ascent",
    statics=dict(
        climb_id=UUID,
        ascent_date=datetime,
        attempts=conint(ge=1),
        public=bool, # TODO: does this need to be a custom api?
    ),
)
