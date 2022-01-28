import logging
from typing import Any, List, Mapping, Optional, TypeVar, Union

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_nameToLevel = {
    'CRITICAL': CRITICAL,
    'FATAL': FATAL,
    'ERROR': ERROR,
    'WARN': WARNING,
    'WARNING': WARNING,
    'INFO': INFO,
    'DEBUG': DEBUG,
    'NOTSET': NOTSET,
}


class MyLogger(object):
    def __init__(self, level: str = "INFO"):
        self.level = _nameToLevel.get(level)
        self.log_format = "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"
        self.date_format = "%Y-%m-%d %H:%M:%S"
        logging.basicConfig(level=self.level,
                            format=self.log_format,
                            datefmt=self.date_format)
        self.logger = logging.getLogger(__name__)

    def info(self, msg: Optional[str] = None):
        self.logger.info(msg)

    def warning(self, msg: Optional[str] = None):
        self.logger.warning(msg)

    def error(self, msg: Optional[str] = None):
        self.logger.error(msg)

    def debug(self, msg: Optional[str] = None):
        self.logger.debug(msg)
