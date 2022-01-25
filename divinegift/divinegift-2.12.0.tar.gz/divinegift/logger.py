from deprecation import deprecated

from divinegift import main, version
# from divinegift import sender

import os
import logging
from logging.handlers import TimedRotatingFileHandler

from typing import List, Dict, Optional


class Logger:
    def __init__(self):
        self.logger: Optional[logging.Logger] = None
        self.log_dir = None
        self.log_name = None
        self.formatter = logging.Formatter('%(levelname)-8s [%(asctime)s] %(message)s')

    def set_log_level_(self):
        self.set_log_level(**main.get_log_param(main.get_args()))

    def set_log_level(self, log_level: str, log_name: str = None, log_dir: str = './logs/', when: str = 'midnight',
                      interval: int = 1, backup_count: int = 7):
        """
            This set up log_level and name of logfile
            :param log_level: String with log_level (e.g. 'INFO')
            :param log_name: Name of file with logs
            :param log_dir: Directory which should keep logs
            :param when: When rotate log
            :param interval: How often
            :param backupCount: How many version need to keep
            :return: None
        """

        self.logger = logging.getLogger('Rotating')
        # Remove all existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % log_level)

        self.logger.setLevel(numeric_level)

        if log_name:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            handler = TimedRotatingFileHandler(os.path.join(log_dir, log_name), when=when, interval=interval,
                                               backupCount=backup_count, encoding='utf-8')
            self.log_name = log_name
            self.log_dir = log_dir
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    def log_debug(self, *args, separator: str = ' '):
        """
        Logging a debug message
        :return: None
        """
        if not self.logger:
            self.set_log_level_()
        self.logger.debug(separator.join([str(x) for x in args]))

    def log_info(self, *args, separator: str = ' '):
        """
        Logging a info
        :param separator: Separator
        :return: None
        """
        if not self.logger:
            self.set_log_level_()
        self.logger.info(separator.join([str(x) for x in args]))

    def log_warn(self, *args, separator: str = ' '):
        """
        Logging a warning
        :param separator: Separator
        :return: None
        """
        if not self.logger:
            self.set_log_level_()
        self.logger.warning(separator.join([str(x) for x in args]))

    def log_err(self, *args, separator: str = ' '):
        """
        Logging an error with monitoring if parameters were filled
        :param separator: Separator
        :return: None
        """
        if not self.logger:
            self.set_log_level_()
        self.logger.exception(separator.join([str(x) for x in args]))

    def log_crit(self, *args, separator: str = ' '):
        if not self.logger:
            self.set_log_level_()
        self.logger.critical(separator.join([str(x) for x in args]))


@deprecated(deprecated_in='2.8.0', current_version=version, details='Use class Logger instead')
def log_debug(*args, separator: str = ' '):
    get_logger().log_debug(*args, separator=separator)


@deprecated(deprecated_in='2.8.0', current_version=version, details='Use class Logger instead')
def log_info(*args, separator: str = ' '):
    get_logger().log_info(*args, separator=separator)


@deprecated(deprecated_in='2.8.0', current_version=version, details='Use class Logger instead')
def log_warning(*args, separator: str = ' '):
    get_logger().log_warn(*args, separator=separator)


@deprecated(deprecated_in='2.8.0', current_version=version, details='Use class Logger instead')
def log_err(*args, separator: str = ' ', src: str = None, mode: List = None, channel: Dict = None):
    get_logger().log_err(*args, separator=separator)


@deprecated(deprecated_in='2.8.0', current_version=version, details='Use class Logger instead')
def log_crit(*args, separator: str = ' '):
    get_logger().log_crit(*args, separator=separator)


def set_loglevel(log_level: str, log_name: str = None, log_dir: str = './logs/',
                 when: str = 'midnight', interval: int = 1, backupCount: int = 7):
    get_logger().set_log_level(log_level, log_name, log_dir, when, interval, backupCount)


logger_ = Logger()


def get_logger():
    return logger_


if __name__ == '__main__':
    pass
