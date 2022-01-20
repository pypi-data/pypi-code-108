from __future__ import annotations
import loguru

logger = None


def set_logger(_logger: loguru.Logger):
    global logger
    logger = _logger


def get_logger(context: str = None):
    return logger.bind(context=context)
