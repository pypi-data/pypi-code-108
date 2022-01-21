import logging
import logging.config
import os

import yaml

fileLogger = logging.getLogger("fileLogger")


def init_logger(conf_file):
    if os.path.exists(conf_file):
        with open(conf_file, 'r') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)


def debug_log(file_name, msg):
    if fileLogger.hasHandlers():
        if len(file_name.strip()) > 0:
            fileLogger.handlers[0].setFileName("debug_" + file_name)
        else:
            fileLogger.handlers[0].setFileName(fileLogger.handlers[0].defaultFileName)
        fileLogger.debug(msg)


def error_log(file_name, msg):
    if fileLogger.hasHandlers():
        if len(file_name.strip()) > 0:
            fileLogger.handlers[0].setFileName("error_" + file_name)
        else:
            fileLogger.handlers[0].setFileName(fileLogger.handlers[0].defaultFileName)
        if isinstance(msg, Exception):
            try:
                fileLogger.error(msg, exc_info=True)
            except Exception:
                fileLogger.error(str(msg))
        else:
            fileLogger.error(str(msg))
