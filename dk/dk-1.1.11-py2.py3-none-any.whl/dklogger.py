"""
Convenience function for installing a module level logger::

     from dk import dklogger
     logger = dklogger.dklogger(__name__, debug=1, info=1)
     logger.setLevel(dklogger.DEBUG)

to prevent logging to stdout, pass `stream=None`
"""

# pylint:disable=W0401,W0621
# W0401: import * (used to grab all logging constants etc.)
# W0621: shadowing logging.debug inside dklogger

import sys
from logging import *   # noqa
from logging import (
    getLogger, StreamHandler, FileHandler, INFO, DEBUG, Formatter
)


def dklogger(name, debug=False, info=False,
             fname=None,
             stream=sys.stdout,
             format='''%(asctime)s %(levelname)-7s
                    %(pathname)s@%(funcName)s:%(lineno)d %(message)s''',
             datefmt='%Y-%m-%d %H:%M:%S'):
    sh = fh = None
    logger = getLogger(name)
    if stream:
        sh = StreamHandler(stream)
        logger.addHandler(sh)
    if fname:
        fh = FileHandler(fname, encoding='utf-8')
        logger.addHandler(fh)
    if format:
        fmt = Formatter(format, datefmt)
        if sh:
            sh.setFormatter(fmt)
        if fh:
            fh.setFormatter(fmt)

    if info:
        logger.setLevel(INFO)
    if debug:
        logger.setLevel(DEBUG)
    return logger
