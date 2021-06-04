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

from app import create_api, VoteDefinition


router = APIRouter(
    tags=["crags"],
)

# TODO: area vote?

create_api(
    router,
    model_name="Crag",
    collection_name="crags",
    item_name="crag",
    voted=[
        VoteDefinition(
            model_name="CragNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        )
    ]
)
