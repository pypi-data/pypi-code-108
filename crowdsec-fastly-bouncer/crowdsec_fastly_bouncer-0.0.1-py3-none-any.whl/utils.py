import logging
import sys


SUPPORTED_ACTIONS = ["ban", "captcha"]


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR: "[%(asctime)s] %(levelname)s - %(message)s",
        logging.WARNING: "[%(asctime)s] %(levelname)s - %(message)s",
        logging.DEBUG: "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        "DEFAULT": "[%(asctime)s] %(levelname)s - %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS["DEFAULT"])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def with_suffix(string: str, **kwargs):
    keys = sorted(list(kwargs.keys()))
    suffix = " ".join([f"{k}={kwargs[k]}" for k in keys])
    return f"{string} {suffix}"


def are_filled_validator(**kwargs):
    for k, v in kwargs.items():
        if v is None:
            raise ValueError(f"{k} is not specified in config")


def get_default_logger():
    logger = logging.getLogger("")
    default_handler = logging.StreamHandler(sys.stdout)
    default_formatter = CustomFormatter()
    default_handler.setFormatter(default_formatter)
    logger.addHandler(default_handler)
    return logger
