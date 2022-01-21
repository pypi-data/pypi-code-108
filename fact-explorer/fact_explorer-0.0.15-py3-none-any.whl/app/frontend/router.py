from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from fact_explorer.app.api.constants import API_RESPONSES
from fact_explorer.config import FRONTEND_SOURCE_PATH
from fact_explorer.config import get_logger


log = get_logger("frontend.router")

router = APIRouter(responses=API_RESPONSES, include_in_schema=False)

# For now as we have only two routes I decided to not do the
# route(/{full_path:path}) magic but rather be explicit in routing
# if we decide to have more pages this decision should be revisited.


@router.get("/")
async def index(request: Request):
    resp = FileResponse(FRONTEND_SOURCE_PATH.joinpath("index.html"))
    return resp


@router.get("/search")
async def search(request: Request):
    resp = FileResponse(FRONTEND_SOURCE_PATH.joinpath("search.html"))
    return resp


@router.get("/favicon.ico")
async def favicon(request: Request):
    resp = FileResponse(FRONTEND_SOURCE_PATH.joinpath("favicon.png"))
    return resp
