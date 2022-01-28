import json
import logging.handlers
import os
from typing import Dict, List, Optional

import pydantic

from .misc import merge

logger = logging.getLogger(__name__)


DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_early_logging():
    """
    Sets up log buffering before logging can be setup!  Logging is often configured in a configuration.
    Some log messages may be emitted before that can be loaded; this especially include log messages about loading
    configuration.
    """
    logging.basicConfig(level=0, handlers=(PreLoggingHandler(),))


def flush_early_logging():
    PreLoggingHandler.flush()


class LogConfig(pydantic.BaseModel):
    log_level: str = "INFO"
    log_unit_levels: Dict[str, str] = {}
    log_format: str = DEFAULT_LOG_FORMAT
    base_logger_dict: Dict = None

    @property
    def _default_base_logger(self) -> Dict:
        return {
            'version': 1,
            # This will always be overwritten; it's here as a placeholder
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    # This will always be overwritten; it's here as a placeholder
                    'format': DEFAULT_LOG_FORMAT
                }
            },
            'handlers': {
                'default': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    "stream": "ext://sys.stderr",
                }
            },
            'loggers': {
                'root': {
                    'handlers': ['default'],
                    # This will always be overwritten; it's here as a placeholder
                    'level': "INFO"
                }
            }
        }

    def dict_config(self, base_logger_dict: Optional[Dict] = None) -> Dict:
        log_dict = self.base_logger_dict or base_logger_dict  or self._default_base_logger
        log_dict = merge(log_dict.copy(), {
            'disable_existing_loggers': False,
            'root': {'handlers': ["default"], 'level': self.log_level},
            'formatters': {'default': {'fmt': DEFAULT_LOG_FORMAT}},
            'loggers': {unit: {'level': level} for unit, level in self.log_unit_levels.items()}
        })
        return log_dict


class PreLoggingHandler(logging.Handler):
    global_buffer: List[logging.LogRecord] = []

    def __init__(self):
        super().__init__()
        self.buffer = self.global_buffer

    def emit(self, record: logging.LogRecord) -> None:
        self.global_buffer.append(record)

    @classmethod
    def flush(cls) -> None:
        messages = cls.global_buffer.copy()
        cls.global_buffer.clear()
        for message in messages:
            logging.getLogger(message.name).log(
                level=message.levelno,
                msg=message.msg,
                exc_info=message.exc_info,
                stack_info=message.stack_info,
                *message.args
            )


def setup_logging(default_level: int = logging.INFO):
    """
    Setup logging for the program.  Rather than using program arguments this will interpret two environment variables
    to set log levels.  Both may be blank in which case the program will log at DEBUG level.  Note that some libraries
    such as sqlalchemy set their own fine grained log level and therefore must be enabled through LOG_LEVELS if you need
    their output.

    LOG_LEVEL sets the default.
    LOG_LEVELS is a json string holding a dictionary mapping logger names to log level names.

    Log messages emitted by this method are deliberately from the root logger to make it clear at the start of the
    program run what is supposed to be in the log without it getting switched off by fine grained logging.
    """
    # Find the default log level from environment variable
    try:
        default_level_name = os.environ["LOG_LEVEL"]
        new_default_level = logging.getLevelName(default_level_name)
        if isinstance(default_level, int):
            default_level = new_default_level
        else:
            default_level_name = logging.getLevelName(default_level)
    except KeyError:
        default_level_name = logging.getLevelName(default_level)

    logging.basicConfig(format=DEFAULT_LOG_FORMAT, level=default_level)

    # We can't log anything before logging.basicConfig so we have to check it again after and log the message here
    if not isinstance(logging.getLevelName(default_level_name), int):
        logger.warning(f"Unknown log level name {default_level_name} in LOG_LEVEL")
    logger.debug(f"Logging configured to default level {logging.getLevelName(default_level)}")

    for logger_name, level_name in json.loads(os.environ.get('LOG_LEVELS', "{}")).items():
        log_level = logging.getLevelName(level_name)
        if not isinstance(log_level, int):
            logger.warning(f"Unknown log level name {level_name} in LOG_LEVELS")
        else:
            logging.getLogger(logger_name).level = log_level
            logger.debug(f"Logging for '{logger_name}' set to {logging.getLevelName(log_level)}")