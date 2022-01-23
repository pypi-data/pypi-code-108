from loguru import logger
from nacl.exceptions import BadSignatureError
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

from discourtesy.followup import FollowupTask


class InteractionRoute(Route):
    def __init__(self):
        super().__init__("/interaction", self.endpoint, methods=["POST"])

    async def endpoint(self, request):
        try:
            signature = request.headers["X-Signature-Ed25519"]
            timestamp = request.headers["X-Signature-Timestamp"]
        except KeyError:
            return PlainTextResponse("Bad Request", status_code=400)

        body = await request.body()

        try:
            request.app.verify_key.verify(
                timestamp.encode() + body, bytes.fromhex(signature)
            )
        except BadSignatureError:
            return PlainTextResponse("Unauthorized", status_code=401)

        interaction = await request.json()

        # Handle requests of T1 PING.

        if interaction["type"] == 1:
            logger.debug("Received T1 PING.")

            return JSONResponse({"type": 1}, status_code=200)

        # Handle requests of T2 APPLICATION_COMMAND.

        if interaction["type"] == 2:
            logger.debug("Received T2 APPLICATION_COMMAND.")

            message, task = await request.app.dispatch.execute_command(
                request.app, interaction
            )

            if task:
                response = {"type": 5}
                followup_task = FollowupTask(task, request.app, interaction)

                return JSONResponse(
                    response, background=followup_task, status_code=200
                )

            response = {"type": 4, "data": message}

            return JSONResponse(response, status_code=200)

        # Handle requests of T3 MESSAGE_COMPONENT

        if interaction["type"] == 3:
            logger.debug("Received T3 MESSAGE_COMPONENT.")

            message = await request.app.dispatch.execute_component(
                request.app, interaction
            )

            response = {"type": 7, "data": message}

            if not message:
                response = {"type": 6}

            return JSONResponse(response, status_code=200)

        # Return 400 Bad Request for requests that didn't get handled.

        return PlainTextResponse("Bad Request", status_code=400)
