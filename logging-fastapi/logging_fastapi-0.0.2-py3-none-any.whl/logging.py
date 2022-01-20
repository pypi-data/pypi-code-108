from __future__ import annotations
from asyncio import create_task, sleep
from contextvars import ContextVar
import json
import sys
import time
import traceback
from cuid import cuid
from loguru import logger as base_logger
from fastapi import FastAPI, Request, Response
import loguru
from starlette.responses import PlainTextResponse
import psutil
import pydash
import schedule
import requests
import inspect
import logging as _logging
import ast


def is_obj_or_dict(obj):
    return inspect.isclass(obj) or type(obj) is dict


request_id_ctx = ContextVar("requestId")
error_ctx = ContextVar("error")
logger = base_logger


def set_logger(_logger: loguru.Logger):
    global logger
    logger = _logger


def get_logger(context: str = None):
    return logger.bind(context=context)


def run_samplers():
    def collect():
        metrics = {}

        memory = psutil.virtual_memory()
        metrics["memory"] = {"used": memory.used, "available": memory.available}

        total_cpu = psutil.cpu_percent()
        metrics["cpu"] = {"load": total_cpu}

        logger.debug(metrics)

    schedule.every(10).seconds.do(collect)


class LokiTransport:
    def __init__(self, loki_options):
        self.url = loki_options["url"] + "/loki/api/v1/push"
        self.base_labels = loki_options["labels"]
        self.headers = {"Content-type": "application/json"}
        self.streams = []
        schedule.every(5).seconds.do(self.send_batch)

    def prepare_json_streams(self, streams):
        json_streams = []
        for stream in streams:
            values = []
            for entry in stream["entries"]:
                values.append([json.dumps(entry["ts_ns"]), entry["line"]])
            json_streams.append({"stream": stream["labels"], "values": values})
        return json_streams

    def prepare_proto_streams(self, streams):
        proto_streams = []
        for stream in streams:
            labels = pydash.clone_deep(stream["labels"])
            proto_labels = "{"
            proto_labels += f'level="{labels["level"]}"'
            del labels["level"]
            for key in labels:
                proto_labels += f',{key}="{labels[key]}"'
            proto_labels += "}"
            proto_streams.append(
                {
                    "labels": proto_labels,
                    "entries": pydash.map_(
                        stream["entries"],
                        lambda entry: {
                            "line": entry["line"],
                            "ts": json.dumps(entry["ts_ns"] / 1000 / 1000),
                        },
                    ),
                }
            )
        return proto_streams

    def send_batch(self):
        if len(self.streams) == 0:
            return
        json_streams = self.prepare_json_streams(self.streams)
        payload = json.dumps({"streams": json_streams})
        self.streams = []
        try:
            requests.post(self.url, data=payload, headers=self.headers)
        except:
            pass

    def collect(self, labels, entry):
        for stream in self.streams:
            if pydash.is_equal(stream["labels"], labels):
                stream["entries"].append(entry)
                return
        new_stream = {"labels": labels, "entries": [entry]}
        self.streams.append(new_stream)

    def entry_from_record(self, record):
        return {"ts_ns": time.time_ns(), "line": record["message"]}

    def write(self, record):

        record = record.record

        level = record["level"].name.lower()
        if level == "warning":
            level = "warn"
        labels = {**self.base_labels, "level": level}

        entry = self.entry_from_record(record)
        self.collect(labels, entry)
        if level == "critical":
            self.send_batch()


def format_exc():
    etype, value, tb = sys.exc_info()
    lines = traceback.format_exception(etype=etype, value=value, tb=tb)

    error = {
        "message": str(value),
        "stack": pydash.map_(
            lines[-2:], lambda line: line.replace("\n", "").replace('"', "'")
        )[::-1],
    }

    return error


def formatter(record):

    context = record["extra"].get("context")
    try:
        record["message"] = json.loads(record["message"])

    except:
        try:
            record["message"] = ast.literal_eval(record["message"])
        except:
            pass
        pass

    request_id = request_id_ctx.get(None)
    if not is_obj_or_dict(record["message"]):
        record["message"] = {"message": record["message"]}

    if context:
        record["message"]["context"] = context
    else:
        record["message"]["context"] = record["function"]

    if request_id:
        record["message"]["requestId"] = request_id

    error = error_ctx.get(None)
    if error:
        record["message"]["stack"] = error["stack"]
        record["message"]["error_message"] = str(error["message"])
        if "name" in error:
            record["message"]["error_name"] = error["name"]
    return record["message"]


class InterceptHandler(_logging.Handler):
    loglevel_mapping = {
        50: "critical",
        40: "error",
        30: "warn",
        20: "info",
        10: "debug",
        0: "notset",
    }

    def emit(self, record):

        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]
        frame, depth = _logging.currentframe(), 2
        while frame.f_code.co_filename == _logging.__file__:
            frame = frame.f_back
            depth += 1
        msg = record.getMessage()
        if "ASGI" in msg:
            return
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def create_logger(console: bool = False, loki=None):
    _logger = base_logger.patch(formatter)
    _logger.remove()

    if console:
        _logger.add(sys.stdout, level="INFO")
    if loki:
        loki_transport = LokiTransport(loki_options=loki)
        _logger.add(loki_transport)

    _logging.basicConfig(handlers=[InterceptHandler()], level=0)
    _logging.getLogger("uvicorn").handlers = []
    _logging.getLogger("uvicorn.access").handlers = []

    return _logger


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

    return json.dumps(to_log)


def log_request_response(req: Request, res: Response):

    to_log = get_info(req, res)

    if res.status_code < 400 and res.status_code >= 200:
        logger.info(to_log)
    else:
        if res.status_code >= 500:
            logger.error(to_log)
        else:
            logger.warning(to_log)


def logging(app: FastAPI, console: bool = False, loki=None):
    logger = create_logger(console, loki)
    set_logger(logger)
    app.logger = logger

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

    run_samplers()

    async def periodic():
        while True:
            schedule.run_pending()
            await sleep(1)

    create_task(periodic())

    class LoggerWriter:
        def __init__(self, level):
            self.level = level
            self._msg = ""
            self.new = True

        def write(self, message):
            self._msg = self._msg + message
            if self.new:
                error_ctx.set(format_exc())
                self.new = False

        def flush(self):
            if self._msg != "":
                msg = error_ctx.get(None)["message"]
                self.level(f"Unhandled Exception - {msg}")
                self.new = True

    sys.stderr = LoggerWriter(logger.critical)
