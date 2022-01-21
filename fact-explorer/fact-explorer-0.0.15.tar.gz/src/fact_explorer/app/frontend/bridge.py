from fastapi.staticfiles import StaticFiles
from starlette.types import Scope
from starlette.responses import Response


class SpaStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            response = await super().get_response(path=".", scope=scope)
        return response
