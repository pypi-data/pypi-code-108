#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
import logging
import os
import sys
import time
import traceback

# LOGGING_LEVEL = logging.INFO
LOGGING_LEVEL = logging.DEBUG
# LOGGING_LEVEL = logging.ERROR


def get_logger(module_name):
    """Logger to stdout.

    Typical use: logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(module_name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOGGING_LEVEL)
    return logger


def log_with_exc_info(logger, e):
    """Log with exception info.

    Common usage when logging at the end of a try/except to identify the
    line number and error type
    """
    # Log the message with the exception info
    logger.error("ERROR::: {}, {}".format(e, get_exception_info()))


def get_exception_info():
    """Get information on a raised exception."""
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    return {
        "traceback": repr(traceback.extract_tb(exc_tb)),
        "exception_type": exc_type,
        "file_name": fname,
        "line_number": exc_tb.tb_lineno,
    }


class DurationLogger:
    def __init__(self, tag: str = ''):
        self.tag = tag
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()

    def duration(self, digs=2):
        return round(self.end_time - self.start_time, digs)

    def log_duration(self, tag=''):
        logging.info(
            "{} {} ::: Duration: = {}s".format(
                tag,
                self.tag,
                self.duration()))
