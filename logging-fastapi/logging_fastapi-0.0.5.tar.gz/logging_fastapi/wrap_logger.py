from __future__ import annotations
import ast
import loguru
import json

from .utils import is_obj_or_dict
from .ctx import request_id_ctx, error_ctx


def pre_formatter(message):

    try:
        message = json.loads(message)["message"]
    except:
        try:
            message = ast.literal_eval(message)
        except:
            pass

    try:
        if is_obj_or_dict(message):
            logObj = message
        else:
            logObj = {}
            logObj["message"] = message
    except:
        pass

    request_id = request_id_ctx.get(None)
    if request_id:
        logObj["requestId"] = request_id

    error = error_ctx.get(None)
    if error:
        logObj["stack"] = error["stack"]
        logObj["error_message"] = str(error["message"])
        if "name" in error:
            logObj["error_name"] = error["name"]

    return json.dumps(logObj)


class WrapLogger:
    original_logger: loguru.Logger

    def __init__(self, original_logger: loguru.Logger) -> None:
        self.original_logger = original_logger

    def info(self, message):
        json_msg = pre_formatter(message)
        return self.original_logger.info(json_msg)

    def critical(self, message):
        json_msg = pre_formatter(message)
        return self.original_logger.critical(json_msg)

    def error(self, message):
        json_msg = pre_formatter(message)
        return self.original_logger.error(json_msg)

    def warning(self, message):
        json_msg = pre_formatter(message)
        return self.original_logger.warning(json_msg)

    def debug(self, message):
        json_msg = pre_formatter(message)
        return self.original_logger.debug(json_msg)

    def opt(self, *args, **kwargs):
        return WrapLogger(self.original_logger.opt(*args, **kwargs))

    def bind(self, *args, **kwargs):
        return WrapLogger(self.original_logger.bind(*args, **kwargs))

    def level(self, *args, **kwargs):
        return self.original_logger.level(*args, **kwargs)

    def log(self, level, message):
        json_msg = pre_formatter(message)
        return self.original_logger.log(level, json_msg)
