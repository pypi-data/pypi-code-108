# pylint: disable=C1801,W1202,C0103

import sys
import traceback
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from exoedge.constants import DEFAULTS
from murano_client.logger import LOG_FORMAT, FORMATTER

if not hasattr(sys.modules.get(__name__), 'LOGGERS'):
    global LOGGERS
    LOGGERS = []

LOG_KWARGS = {
    'format': LOG_FORMAT,
    'level': getattr(logging, DEFAULTS['debug'].upper())
}

if DEFAULTS['log-filename'] in ['stdout', 'stderr']:
    DEFAULTS['log-filename'] = getattr(sys, DEFAULTS['log-filename'])
    LOG_KWARGS['stream'] = DEFAULTS['log-filename']
else:
    LOG_KWARGS['filename'] = DEFAULTS['log-filename']
    LOG_KWARGS['filemode'] = 'a'

logging.basicConfig(**LOG_KWARGS)
logging.getLogger().propagate = False
logging.getLogger().setLevel(getattr(logging, DEFAULTS['debug'].upper()))
LOGGERS.append(logging.getLogger())

def log_exceptions(ex_cls, ex, tb):
    _tb = ''
    for e in traceback.format_tb(tb):
        _tb += e
    logging.critical('edged logging unhandled exception: \n{}{}'
                     .format(_tb, ex))
sys.excepthook = log_exceptions

def getLogger(*args, **kwargs):
    global LOGGERS
    name = args[0]
    if not name.startswith("exoedge"):
        name = 'exoedge.' + name
    log = logging.getLogger(name=name)
    if kwargs.get('level') != None and isinstance(kwargs.get('level'), int):
        level = kwargs.get('level') or logging.DEBUG
    else:
        level = LOG_KWARGS.get('level')
    log.setLevel(level)
    log.info("Starting logger {}({}): {}".format(name, log.level, log))
    if not len(log.handlers) and DEFAULTS['log-filename'] not in [sys.stdout, sys.stderr]:
        rfh = RotatingFileHandler(
            kwargs.get('log-filename') or DEFAULTS['log-filename'],
            maxBytes=kwargs.get('log-max-bytes') or 1024*1000,
            backupCount=kwargs.get('log-max-backups') or 3,
        )
        rfh.setFormatter(FORMATTER)
        log.addHandler(rfh)

    elif not len(log.handlers) and DEFAULTS['log-filename'] in [sys.stdout, sys.stderr]:
        streamh = logging.StreamHandler(DEFAULTS['log-filename'])
        streamh.setFormatter(FORMATTER)
        log.addHandler(streamh)

    log.propagate = False
    LOGGERS.append(log)
    return log

def getExoEdgeLoggers():
    global LOGGERS
    return LOGGERS