from starlette.responses import PlainTextResponse
from starlette.routing import Route


class IndexRoute(Route):
    def __init__(self):
        super().__init__("/", self.endpoint)

    async def endpoint(self, _):
        response = "This instance of Discourtesy is running!"
        return PlainTextResponse(response)
