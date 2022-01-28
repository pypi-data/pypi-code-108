import os
import logging
import datetime
import sys
from pathlib import Path

def get_logger(name: str = None):
    LOG_DIR = Path.home() / 'Logs' / 'welo365'
    LOG_DIR.mkdir(exist_ok=True)
    LOGGER_NAME = f"{name}.logger" if name else 'logger'
    logfile = os.path.join(LOG_DIR, f"{datetime.datetime.today().strftime('%Y%m%d')}.log")
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    fh = logging.FileHandler(logfile)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger