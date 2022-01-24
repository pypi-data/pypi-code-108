import logging
import os
import sys

from logging import Formatter
from logging.handlers import RotatingFileHandler

DEF_FMT = '"%(asctime)-15s|%(levelname)s:%(name)s|%(filename)s:%(lineno)d|%(message)s"'
DEF_FMT_JSON = '{"asctime":"%(asctime)-15s", "levelname":"%(levelname)s", "filename_and_line":"%(filename)s:' +\
               '%(lineno)d", "process_and_thread":"%(process)d:%(thread)d", "message":"%(message)s"}'
DATE_FMT = "%Y-%m-%d %H:%M:%S:%s"

if os.getenv("FABRIQUE_LOGGER_LEVEL") != "DEBUG":
    LEVEL = logging.INFO
else:
    LEVEL = logging.DEBUG


class FileLogger(object):
    @classmethod
    def make_logger(cls, client_id,
                    level=LEVEL,
                    fmt=DEF_FMT,
                    datefmt=DATE_FMT):
        logger = logging.getLogger()
        logger.setLevel(level)
        h = RotatingFileHandler('/var/log/fabrique/{}.log'.format(client_id), 'a', 300000, 5)
        f = Formatter(fmt=fmt, datefmt=datefmt)
        h.setFormatter(f)
        logger.addHandler(h)
        return logger


class StdOutLogger(object):
    @classmethod
    def make_logger(cls, client_id='',
                    level=LEVEL,
                    fmt=DEF_FMT,
                    datefmt=DATE_FMT):
        print(f'client_id = {client_id}')  # deprecated
        logger = logging.getLogger()
        logger.setLevel(level)
        h = logging.StreamHandler(sys.stdout)
        f = Formatter(fmt=fmt, datefmt=datefmt)
        h.setFormatter(f)
        logger.addHandler(h)
        return logger


Logger = StdOutLogger
