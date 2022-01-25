import logging
import sys
from .storage import get_logger
from .ctx import request_id_ctx, error_ctx
from .utils import format_exc


class InterceptHandler(logging.Handler):
    level = 0
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        5: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record: logging.LogRecord):
        logger = get_logger()

        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]
        if level == "TRACE":
            level = "DEBUG"

        frame, depth = logging.currentframe(), 3
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        req = request_id_ctx.get(None)
        if req and level == "ERROR":
            return
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class LoggerWriter:
    def __init__(self):
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
            logger = get_logger()
            logger.critical(f"Unhandled Exception - {msg}")
            self.new = True


def intercept_std_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=10)
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    sys.stderr = LoggerWriter()
