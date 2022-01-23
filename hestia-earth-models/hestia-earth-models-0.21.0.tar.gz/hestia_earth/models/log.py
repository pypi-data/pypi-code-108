import os
import logging


def _add_handler(logger: logging.Logger, formatter: logging.Formatter, handler: logging.Handler):
    handler.setFormatter(formatter)
    logger.addHandler(handler)


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logger = logging.getLogger('hestia_earth.models')
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
    handler.setLevel(logging.getLevelName('DEBUG'))
    _add_handler(logger, formatter, handler)


_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s')
_add_handler(logger, _formatter, logging.StreamHandler())

LOG_FILENAME = os.getenv('LOG_FILENAME')
if LOG_FILENAME is not None:
    log_to_file(LOG_FILENAME)


def debugRequirements(**kwargs):
    logger.debug(', '.join([f"{key}={value}" for key, value in kwargs.items()]))


def debugMissingLookup(lookup_name: str, row: str, row_value: str, col: str, value):
    if value is None:
        logger.error('Missing lookup=%s, %s=%s, column=%s', lookup_name, row, row_value, col)
