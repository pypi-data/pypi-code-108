from sanic.log import logger
from sanic.exceptions import NotFound


async def catch_404s(request, exception):
    logger.error(f"404 error. Exception: {exception}")
    raise NotFound(message=f"Incorrect route: {request.url}", status_code=404)


async def catch_user_code_errors(request, exception):
    logger.error('User run function failed. Adding "x-ms-run-function-failed" header.')
    request.headers.add("x-ms-run-function-failed", "True")  # TODO: Change to appropriate name in FE
    raise exception


async def catch_triton_inference_errors(request, exception):
    logger.error(f"Triton inference request failed with {exception}")
    raise exception
