import argparse
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import RedirectResponse
from pathlib import Path
import uvicorn

from app.routers import (
    approaches,
    ascents,
    beta_videos,
    climbs,
    comments,
    crag_photos,
    crags,
    external_topo_links,
    grades,
    images,
    lines,
    parkings,
    quick_search,
    search_climbs,
    sectors,
    users,
)


app = FastAPI(
    title="opencrags-rest-api",
    description=" ".join([
        "Open database of boulder problems and sport routes. See",
        "<a href='https://github.com/opencrags/opencrags-rest-api'>github</a>",
        "for more information.",
    ]),
    version=Path("VERSION").read_text().strip(),
)

# CORS errors instead of seeing internal exceptions
# https://stackoverflow.com/questions/63606055/why-do-i-get-cors-error-reason-cors-request-did-not-succeed
cors = CORSMiddleware(
    app=app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=status.HTTP_303_SEE_OTHER, include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.get("/version", status_code=status.HTTP_200_OK, response_model=str, include_in_schema=True)
def get_api_version():
    return Path("VERSION").read_text()


app.include_router(approaches.router)
app.include_router(ascents.router)
app.include_router(beta_videos.router)
app.include_router(climbs.router)
app.include_router(comments.router)
app.include_router(crag_photos.router)
app.include_router(crags.router)
app.include_router(external_topo_links.router)
app.include_router(grades.router)
app.include_router(images.router)
app.include_router(lines.router)
app.include_router(parkings.router)
app.include_router(quick_search.router)
app.include_router(search_climbs.router)
app.include_router(sectors.router)
app.include_router(users.router)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    uvicorn.run("app.main:cors", host=args.host, port=args.port, reload=args.reload)
