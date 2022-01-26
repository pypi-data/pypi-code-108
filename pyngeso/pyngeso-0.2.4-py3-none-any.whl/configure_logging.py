import logging
import sys


def setup_logger(logger: logging.Logger) -> logging.Logger:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s.%(module)s.%(funcName)s.%(lineno)s: "
        "%(message)s"
    )
    logger.setLevel(logging.DEBUG)

    # logging to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
