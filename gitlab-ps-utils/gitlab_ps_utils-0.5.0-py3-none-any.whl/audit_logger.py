import logging
from os.path import exists

loggers = {}
log_file_format = \
    "[%(asctime)s][%(levelname)s]| %(message)s"


def audit_logger(name, app_path='.', log_dir='data/logs'):
    name = name + "_audit"
    global loggers
    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        stderr_log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            log_file_format, datefmt="%d %b %Y %H:%M:%S")
        log_dir = f'{app_path}/{log_dir}'
        if exists(log_dir):
            log_path = f'{log_dir}/audit.log'
            file_log_handler = logging.FileHandler(log_path)
            file_log_handler.setFormatter(formatter)
            logger.addHandler(file_log_handler)
        stderr_log_handler.setFormatter(formatter)
        logger.addHandler(stderr_log_handler)
        loggers[name] = logger

        return logger
