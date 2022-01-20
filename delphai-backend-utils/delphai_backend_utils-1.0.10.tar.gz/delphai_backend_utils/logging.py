
from logging import error, warn, info, debug  # noqa: F401
from sys import exc_info
from traceback import format_tb

import coloredlogs
from logging.config import dictConfig
from delphai_backend_utils.config import get_config


def _configure_logging():
    logging_config = get_config('logging')
    standard_format = logging_config['formatters']['standard']
    dictConfig(logging_config)
    coloredlogs.install(fmt=standard_format['format'], datefmt=standard_format['datefmt'])


_configure_logging()


def error_with_traceback():
    """
    Writes to log an occured exception with a last line of traceback
    """
    einfo = exc_info()
    exc_class = einfo[0].__name__
    exc_descr = str(einfo[1])
    traceback = format_tb(einfo[2])
    traceback = '\n' + traceback[-1].strip() if traceback else ''
    error(f'{exc_class}: {exc_descr}{traceback}')
