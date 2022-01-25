import pathlib

import starlette
import starlette.requests
import starlette.responses


async def home(request: starlette.requests):
    template = pathlib.Path(__file__).parent.parent.joinpath("templates").joinpath("home.html")
    with open(template) as template:
        return starlette.responses.HTMLResponse(template.read())
