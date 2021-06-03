from fastapi import APIRouter, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
from uuid import UUID, uuid4
import io
import base64
import json
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Union, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, create_model
from typing import Any

from app import create_api, Voted


router = APIRouter(
    tags=["crags"],
)


create_api(
    router,
    model_name="Crag",
    collection_name="crags",
    item_name="crag",
    voted=[
        Voted(
            model_name="CragNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        )
    ]
)

# POST /crags
# POST /crags/{crag_id}/votes
# POST /crags/{crag_id}/votes


# this wont work when there are multiple thing to vote about?
# POST /climbs/{climb_id}/gradeVotes
# POST /climbs/{climb_id}/ratings

# How to generalize this?

# Crag
#   name-vote
#   area-vote

# Sector
#   name-vote
#   area-vote

# Climb
#   name-vote
#   coordinate-vote
#   grade-vote
#   rating-vote

# Parking
#   coordinate-vote

# Approach
#   path-vote

# create_model(
#     "Climb",
#     votes={
#         "name_vote": str,
#         "coordinate_vote": Coordinate,
#         "grade_vote": Grade,
#         "rating_vote": int,
#     }
# )

