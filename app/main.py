from fastapi import FastAPI, Response, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
import random
import io
from uuid import UUID
import base64
import json
from pathlib import Path
import PIL
from pydantic import BaseModel, validator, Field
from enum import Enum
from typing import List, Union, Literal, Optional

from app.routers import (
    approaches,
    parkings,
    lines,
    ascents,
    climbs,
    crags,
    images,
    quick_search,
    sectors,
    grades,
)


app = FastAPI(
    title="opencrags-rest-api",
    description="Database of boulder problems and lead routes",
    version=Path("VERSION").read_text().strip(),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=status.HTTP_303_SEE_OTHER, include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


app.include_router(crags.router)
app.include_router(sectors.router)
app.include_router(images.router)
app.include_router(climbs.router)
app.include_router(lines.router)
app.include_router(ascents.router)
app.include_router(grades.router)
app.include_router(approaches.router)
app.include_router(parkings.router)
app.include_router(quick_search.router)
