import logging
import os

from simses.commons.config.log import LogConfig


class Logger:

    """
    SimSES Logger with possibility to write logs to console and file. Logger is configurable via logger.ini in config.
    """

    __format: str = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    __filename: str = 'simses.log'
    __path: str = os.getcwd() + '/'

    def __init__(self, name: str, log_level: int = 0):
        log_config: LogConfig = LogConfig()
        log_level = log_config.log_level if log_level == 0 else log_level
        # logger and handler
        logger = logging.getLogger(name.split('.')[-1].upper().strip('_'))
        file_handler = logging.FileHandler(self.__path + self.__filename)
        stream_handler = logging.StreamHandler()
        # setting log level
        logger.setLevel(log_level)
        file_handler.setLevel(log_level)
        stream_handler.setLevel(log_level)
        # setting format
        formatter = logging.Formatter(fmt=self.__format)
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        # add handler
        if log_config.log_to_console:
            logger.addHandler(stream_handler)
        if log_config.log_to_file:
            logger.addHandler(file_handler)
        self.logger: logging.Logger = logger

    def info(self, msg) -> None:
        self.logger.info(msg)

    def warn(self, msg) -> None:
        self.logger.warning(msg)

    def error(self, msg) -> None:
        self.logger.error(msg)

    def debug(self, msg) -> None:
        self.logger.debug(msg)

    def close(self) -> None:
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
