from typing import Any, Dict
from fastapi import FastAPI


from fact_explorer.app.db.db_session import db_instance as database_instance
from fact_explorer.app.frontend.bridge import SpaStaticFiles
from fact_explorer.app.api.router import router as api_router
from fact_explorer.app.api.registry import router as registry_router
from fact_explorer.app.frontend.router import router as frontend_router
from fact_explorer.app.business.registry import prewarm_caches
from fact_explorer.config import FRONTEND_SOURCE_PATH
from fact_explorer import __version__ as explorer_version
from os import environ as env

app = FastAPI()

# The order of these includes and definitions is important here.
# Later routes will overwrite earlier ones.
app.include_router(api_router)
app.include_router(registry_router)
app.include_router(frontend_router)


@app.get("/health-check")
async def health_check() -> Dict[str, Any]:
    # See: https://tools.ietf.org/id/draft-inadarei-api-health-check-05.html
    return {
        "status": "pass",
        "version": "1",
        "releaseId": str(explorer_version),
        "notes": [""],
        "output": "",
        "checks": {},
    }


app.mount(
    "/",
    SpaStaticFiles(
        directory=str(FRONTEND_SOURCE_PATH),
        html=True,
    ),
    name="Next SPA",
)


@app.on_event("startup")
async def startup() -> None:
    if env.get("DISABLE_CACHE_PREWARM"):
        pass
    else:
        await prewarm_caches()

    await database_instance.connect()
    app.state.db = database_instance
