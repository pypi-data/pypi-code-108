import time
from cuid import cuid
from fastapi import Request, Response
from starlette.responses import PlainTextResponse

from .storage import get_logger
from .ctx import error_ctx, request_id_ctx
from .utils import format_exc


def get_info(req: Request, res: Response):
    status = res.status_code
    method = req.method
    uri = req.url.path
    message = f"HTTP request served - {status} - {method} - {uri}"
    to_log = {
        "message": message,
        "remote_addr": req.client.host,
        "timestamp": time.time(),
        "request": {
            "time": req.state.time,
            "method": method,
            "hostname": req.url.hostname,
            "uri": uri,
            "user_agent": req.headers.get("user-agent"),
            "referer": req.headers.get("referer"),
        },
        "response": {"status": status, "size": int(res.headers.get("Content-Length"))},
    }

    return to_log


def log_request_response(req: Request, res: Response):
    logger = get_logger("HttpInterceptor")
    to_log = get_info(req, res)

    if res.status_code < 400 and res.status_code >= 200:
        logger.info(to_log)
    else:
        if res.status_code >= 500:
            logger.error(to_log)
        else:
            logger.warning(to_log)


def apply_middleware(app):
    @app.exception_handler(Exception)
    async def validation_exception_handler(req, exc: Exception):
        res = PlainTextResponse("Internal Server Error", status_code=500)
        req.state.time = time.time() * 1000 - req.state.start_time
        error_ctx.set(format_exc())
        log_request_response(req, res)
        return res

    @app.middleware("http")
    async def logger_middleware(req: Request, call_next):
        request_id_ctx.set(cuid())
        req.state.start_time = time.time() * 1000
        res = await call_next(req)
        req.state.time = time.time() * 1000 - req.state.start_time
        log_request_response(req, res)
        return res
