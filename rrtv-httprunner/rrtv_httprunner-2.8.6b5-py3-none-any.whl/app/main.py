import uvicorn
from fastapi import FastAPI

from rrtv_httprunner import __version__
from rrtv_httprunner.app.routers import deps, debugtalk, debug, utils

app = FastAPI()


@app.get("/hrun/version")
async def get_hrun_version():
    return {"code": 0, "message": "success", "result": {"HttpRunner": __version__}}


app.include_router(deps.router)
app.include_router(debugtalk.router)
app.include_router(debug.router)
app.include_router(utils.router)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host="127.0.0.1", port=8000, reload=True, debug=True)
