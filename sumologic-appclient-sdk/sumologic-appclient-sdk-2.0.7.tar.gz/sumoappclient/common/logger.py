# -*- coding: future_fstrings -*-
import sys
import logging
import logging.handlers as handlers

from sumoappclient.common.ctocstatus import HealthStatusHandler
from sumoappclient.common.utils import get_normalized_path
import os

EXCLUDED_MODULE_LOGGING = ("requests", "urllib3")
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(threadName)s | %(filename)s | %(message)s"
LOG_FILEPATH = "/tmp/sumoapiclient.log"
ROTATION_TYPE = "D"  # use H for hourly W6 for weekly(ie Sunday)
ROTATION_INTERVAL = 10  # in hours
ENABLE_CONSOLE_LOG = True
ENABLE_LOGFILE = True


def get_logger(name, LOG_FORMAT=LOG_FORMAT, LOG_FILEPATH=LOG_FILEPATH, ROTATION_TYPE=ROTATION_TYPE,
               ROTATION_INTERVAL=ROTATION_INTERVAL, ENABLE_LOGFILE=ENABLE_LOGFILE,
               ENABLE_CONSOLE_LOG=ENABLE_CONSOLE_LOG, LOG_LEVEL="INFO", BACKUP_COUNT=5, force_create=False, pkg_name=None):
    name = name or __name__
    log = logging.getLogger(name)
    if (not log.handlers) or force_create:
        if force_create:
            # removing existing handlers
            for hdlr in log.handlers:
                log.removeHandler(hdlr)
        if os.getenv("DEBUG"):
            LOG_LEVEL = "DEBUG"

        log_level = logging.getLevelName(LOG_LEVEL)
        log.setLevel(log_level)
        if pkg_name:
            LOG_FORMAT = pkg_name + " | " + LOG_FORMAT
        logFormatter = logging.Formatter(LOG_FORMAT)

        c2c_base_url = os.getenv("BASE_URL", None)
        if c2c_base_url:
            # c2c framework so enabling c2chealth handler
            ctocLogFormatter = logging.Formatter("%(message)s")
            healthStatusHandler = HealthStatusHandler(c2c_base_url)
            healthStatusHandler.setFormatter(ctocLogFormatter)
            log.addHandler(healthStatusHandler)

        if ENABLE_CONSOLE_LOG:
            consoleHandler = logging.StreamHandler(sys.stdout)
            consoleHandler.setFormatter(logFormatter)
            log.addHandler(consoleHandler)

        if ENABLE_LOGFILE:
            LOG_FILEPATH = get_normalized_path(LOG_FILEPATH)
            filehandler = handlers.TimedRotatingFileHandler(
                LOG_FILEPATH, backupCount=BACKUP_COUNT,
                when=ROTATION_TYPE, interval=ROTATION_INTERVAL,
                # encoding='bz2',  # uncomment for bz2 compression
            )
            # filehandler = logging.FileHandler()
            filehandler.setFormatter(logFormatter)
            log.addHandler(filehandler)

        #disabling logging for requests/urllib3
        for module_name in EXCLUDED_MODULE_LOGGING:
            logging.getLogger(module_name).setLevel(logging.WARNING)
    return log
