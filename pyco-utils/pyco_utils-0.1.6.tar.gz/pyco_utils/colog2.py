import os
import sys
import json
import shutil
import datetime
from pprint import pformat, pprint

import logging
from collections import OrderedDict
from pyco_utils.colog import getLogger

##############################################################
##############################################################

glogger = None
NowStr = lambda fmt="%Y-%m-%d_%H%M": datetime.datetime.now().strftime(fmt)


def get_logger2(logger_name, auto_strip=True, set_as_global=False, logdir="./logs", stdout=True, **kwargs):
    now = NowStr()
    if auto_strip:
        logger_name = os.path.basename(logger_name).split(".")[0].split("_")[-1]
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    log_fn = f"{logger_name}.{now}.{os.getpid()}.log"
    logfile = os.path.join(logdir, log_fn)
    logger2 = getLogger(
        logger_name,
        logfile=logfile,
        stdout=stdout,
        **kwargs
    )
    print("LogFile:", logfile, os.path.abspath(logfile))
    if set_as_global:
        global glogger
        glogger = logger2

    return logger2


def log(*args, stacklevel=2, log_level=50, **kwargs):
    # _log(*args, **kwargs, logger_name=logger.name, level=50, stacklevel=3)
    # logger = getLogger(logger_name, **kwargs)
    result = kwargs.pop('result', None)
    sep = "\t"
    msg = sep.join(map(str, args))
    if kwargs:
        msg += "\n" + pformat(kwargs, indent=2, width=120)
    if result is not None:
        msg += '\n[result] : \n\t{}'.format("\n\t".join(result.split("\n")))
    if sys.version_info > (3, 8, 0):
        ## Changed in version 3.8: The stacklevel parameter was added.
        glogger.log(log_level, msg, stacklevel=stacklevel)
    else:
        glogger.log(log_level, msg)


####################################################
####################################################
def _get_print_log():
    env_k = "PYCO_PRINT_LOG"
    env_v = os.environ.get(env_k)
    if env_v != "print":
        try:                             
            from pyco_utils import get_parent_dir
            m_prj_dir = get_parent_dir('.', subdir=".git") or ".."
            LoggerDir = os.environ.get("LOGGER_DIR", f"{m_prj_dir}/logs")
            LoggerName = os.environ.get("LOGGER_NAME", f"CoLog")

            global glogger
            glogger = get_logger2(LoggerName, set_as_global=True, logdir=LoggerDir)

            def _print_log(*args, **kwargs):
                # print(*args, kwargs)
                log(*args, **kwargs, stacklevel=4)

            _print_log(f"init Logger: {glogger.name}", logger_dir=LoggerDir)
            return _print_log
        except Exception as e:
            print("failed", e)

    print(f'[ENV] ${env_k} = "{env_v}"')

    def _print_log(*args, **kwargs):
        print(*args, kwargs)

    return _print_log


print_log = _get_print_log()
