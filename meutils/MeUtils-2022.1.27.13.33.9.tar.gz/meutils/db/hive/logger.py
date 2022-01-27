import logging


def init_logger_by_name(logger_name="easydata"):
    # ref: https://docs.python.org/3/howto/logging-cookbook.html#multiple-handlers-and-formatters
    # get base logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # set log formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # add straem handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    logger.addHandler(ch)


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)

    return logger


def reset_logger_level(logger_name, level):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)


def init_logger():
    init_logger_by_name("easydata")
    reset_logger_level("pyhive", logging.WARNING)
    reset_logger_level("kazoo", logging.WARNING)
