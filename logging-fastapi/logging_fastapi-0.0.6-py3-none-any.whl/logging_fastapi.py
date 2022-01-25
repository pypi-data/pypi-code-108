import json
import sys
from asyncio import create_task, sleep

import schedule
from fastapi import FastAPI
from loguru import logger as base_logger


from .otel import create_tracer, instrument_app
from .intercept_std_logging import intercept_std_logging
from .loki_transport import LokiTransport
from .request_response import apply_middleware
from .sampler import run_samplers
from .storage import set_logger
from .wrap_logger import WrapLogger


def attach_context(record):
    try:
        logObj = json.loads(record["message"])
    except:
        return

    context = record["extra"].get("context")
    if context:
        logObj["context"] = context
    else:
        logObj["context"] = record["function"]

    record["message"] = logObj


def create_logger(service_name, console: bool = False, loki=None):
    logger = base_logger.patch(attach_context).opt(depth=1)
    logger.remove()
    logger.level("METRICS", no=1, color="<blue>")
    if console:
        logger.add(sys.stdout, level="INFO")
    if loki:
        loki_transport = LokiTransport(loki_options=loki, service_name=service_name)
        logger.add(loki_transport, level="METRICS")
    return WrapLogger(logger)


def run_scheduler():
    async def periodic():
        while True:
            schedule.run_pending()
            await sleep(1)

    create_task(periodic())


def logging(app: FastAPI, service_name, console: bool = False, loki=None, tempo=None):

    logger = create_logger(service_name, console, loki)
    set_logger(logger)
    app.logger = logger
    apply_middleware(app)
    run_samplers()
    run_scheduler()
    intercept_std_logging()
    if tempo is not None:
        instrument_app(app)
        create_tracer(service_name, tempo)
