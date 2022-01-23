import os
import logging

from hestia_earth.aggregation.utils import sum_values


def _add_handler(logger: logging.Logger, formatter: logging.Formatter, handler: logging.Handler):
    handler.setFormatter(formatter)
    logger.addHandler(handler)


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logger = logging.getLogger('hestia_earth.aggregation_engine')
logger.setLevel(logging.getLevelName(LOG_LEVEL))


def log_to_file(filepath: str):
    """
    By default, all logs are saved into a file with path stored in the env variable `LOG_FILENAME`.
    If you do not set the environment variable `LOG_FILENAME`, you can use this function with the file path.

    Parameters
    ----------
    filepath : str
        Path of the file.
    """
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", '
        '"filename": "%(filename)s", "message": "%(message)s"}',
        '%Y-%m-%dT%H:%M:%S%z')
    handler = logging.FileHandler(filepath, encoding='utf-8')
    handler.setLevel(logging.getLevelName(LOG_LEVEL))
    _add_handler(logger, formatter, handler)


_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s')
_add_handler(logger, _formatter, logging.StreamHandler())

LOG_FILENAME = os.getenv('LOG_FILENAME')
if LOG_FILENAME is not None:
    log_to_file(LOG_FILENAME)


def debugRequirements(**kwargs):
    logger.debug(', '.join([f"{key}={value}" for key, value in kwargs.items()]))


def debugWeights(weights: dict):
    total_weight = sum_values(v.get('weight') for v in weights.values()) or 100
    for id, weight in weights.items():
        value = weight.get('weight')
        logger.debug('id=%s, weight=%s, ratio=%s/%s', id, value * 100 / total_weight, value, total_weight)
