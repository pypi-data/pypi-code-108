import json
import pickle
from typing import Any, Optional
from uuid import UUID

import numpy as np
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse, Response, PlainTextResponse

from spell.serving.exceptions import BadAPIResponse
from spell.serving.types import PredictorResponse


async def create_pickle_response(content: Any, tasks: Optional[BackgroundTasks]) -> Response:
    status_code = 200 if not isinstance(content, Response) else content.status_code
    try:
        content = pickle.dumps(content)
    except (TypeError, pickle.PickleError) as e:
        raise BadAPIResponse(f"Response must be picklable. {e}")
    return Response(
        content=content,
        media_type="application/octet-stream",
        background=tasks,
        status_code=status_code,
    )


async def wrap_response(response: PredictorResponse, tasks: Optional[BackgroundTasks] = None) -> Response:
    if isinstance(response, bytes):
        return Response(content=response, media_type="application/octet-stream", background=tasks)
    elif isinstance(response, str):
        return PlainTextResponse(content=response, background=tasks)
    elif isinstance(response, (int, float, UUID)):
        return PlainTextResponse(content=str(response), background=tasks)
    elif isinstance(response, np.generic):
        return PlainTextResponse(content=str(response.item()), background=tasks)
    elif isinstance(response, np.ndarray):
        return JSONResponse(response.tolist(), background=tasks)
    elif isinstance(response, Response):
        if tasks is not None and tasks.tasks:
            if response.background:
                response.background.tasks += tasks.tasks
            else:
                response.background = tasks
        return response
    else:
        try:
            return SpellJSONResponse(response, background=tasks)
        except Exception as e:
            raise BadAPIResponse(
                f"Invalid response. Got untranslatable {type(response)} return type. "
                "Return an object that is JSON-serializable (including its "
                "nested fields), a bytes object, a string, or a "
                "starlette.responses.Response object"
            ) from e


class SpellJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=ResponseJSONEncoder,
        ).encode("utf-8")


class ResponseJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
