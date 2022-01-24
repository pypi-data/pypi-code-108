from typing import IO, Union
import os
import logging

DEFAULT_FMT = "%(asctime)-15s | %(levelname)s | %(module)s: %(message)s"
DEFAULT_FILENAME = "log/log.log"


def get_logger(
    name: str = None,
    fmt: str = DEFAULT_FMT,
    filename: str = DEFAULT_FILENAME,
    stream: IO[str] = None,
    level: int = logging.INFO,
):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler: Union[logging.StreamHandler, logging.FileHandler]

    if filename:
        dirt = os.path.dirname(filename)
        if dirt and not os.path.exists(dirt):
            os.makedirs(dirt)

        handler = logging.FileHandler(filename)
    else:
        handler = logging.StreamHandler(stream=stream)

    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

    return logger
