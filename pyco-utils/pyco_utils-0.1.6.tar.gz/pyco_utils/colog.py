import os
import logging
from logging.handlers import RotatingFileHandler
from pprint import pformat
from functools import wraps
from ._format import pf_echo, pf_response

fmt_str = '[%(asctime)s]%(module)s - %(funcName)s - %(message)s'
fmt = logging.Formatter(fmt_str)

_log_manager = {}


def file_hdl(fmt=fmt, level=logging.INFO, logfile='.log'):
    hdl = logging.FileHandler(filename=logfile, mode='a+')
    hdl.setFormatter(fmt)
    hdl.setLevel(level)
    return hdl


def stream_hdl(fmt=fmt, level=logging.INFO):
    hdl = logging.StreamHandler()
    hdl.setFormatter(fmt)
    hdl.setLevel(level)
    return hdl


def rotating_file_hdl(fmt=fmt,
                      level=logging.INFO,
                      logfile='.log',
                      maxBytes=10 * 1024 * 1024,
                      backupCount=5,
                      **kwargs
                      ):
    hdl = RotatingFileHandler(logfile, maxBytes=maxBytes, backupCount=backupCount)
    hdl.setLevel(level)
    hdl.setFormatter(fmt)
    return hdl


def initRotateLogger(name: str,
                     fmt=fmt,
                     level=logging.DEBUG,
                     stdout=False,
                     logdir=None,
                     logfile='.log',
                     **kwargs
                     ):
    logger = logging.getLogger(name)

    if stdout:
        hdl_stream = stream_hdl(fmt, level)
        logger.addHandler(hdl_stream)

    if logdir and os.path.exists(logdir):
        logfile = os.path.join(logdir, logfile)
    hdl_file = rotating_file_hdl(fmt=fmt, level=level, logfile=logfile, **kwargs)
    logger.addHandler(hdl_file)
    return logger


def getLogger(name: str, **kwargs):
    # single RotateLogger
    logger = _log_manager.get(name, None)
    if logger is None:
        logger = initRotateLogger(name, **kwargs)
        _log_manager[name] = logger
    return logger


def log(*args, logger_name="LOG", level=logging.INFO, **kwargs):
    logger = getLogger(logger_name, **kwargs)
    result = kwargs.pop('result', None)
    msg = "{} {}".format(pformat(args), pformat(kwargs))
    if result is not None:
        msg += '\n[result] : {}'.format(result)
    logger.log(level, msg)


def log_func(logger_name="LOG", level=logging.INFO, pf=pformat, **options):
    """
    :param pf: custom format result, eg: pf_response
    :param options: logger Options
    :return: Any Result of Func
    """
    logger = getLogger(logger_name, **options)

    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            p1 = pf_echo(func, *args, **kwargs)
            resp = func(*args, **kwargs)
            logger.log(level, "{}\n[result]: {}".format(p1, pf(resp)))
            return resp

        return wrapper

    return deco
