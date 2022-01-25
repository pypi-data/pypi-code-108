from fastapi import APIRouter

from rrtv_httprunner.runner import HttpRunner

router = APIRouter()
runner = HttpRunner()


@router.get("/hrun/utils/eval", tags=["debug"])
async def utils_eval(data):
    try:
        return eval(data)
    except:
        return None
