from distutils.log import Log
from os import getenv
from os import getenv
from ingeniictl.logger import Logger

II_LOG_ENABLE_COLORS = bool(int(getenv("II_LOG_ENABLE_COLORS", 1)))
II_LOG_ENABLE_DATETIME_PREFIX = bool(int(getenv("II_LOG_ENABLE_DATETIME_PREFIX", 1)))
log_client = Logger(
    enable_colors=II_LOG_ENABLE_COLORS,
    enable_datetime_prefix=II_LOG_ENABLE_DATETIME_PREFIX,
)
