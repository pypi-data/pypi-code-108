from .func import *
from .logger import logger


def no_none_filter(data: dict):
    return dict(list(filter(lambda item:item[1] is not None, list(data.items()))))
