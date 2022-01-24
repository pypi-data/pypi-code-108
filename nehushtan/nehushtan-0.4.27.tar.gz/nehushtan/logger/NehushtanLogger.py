#  Copyright (c) 2020. Sinri Edogawa

import json
import logging
import logging.handlers
import sys
import warnings
from typing import Iterable


class NehushtanLogger:
    """
    A Logger Class For Shovel
    DEPRECATED SINCE 0.2.5.
    """

    def __init__(
            self,
            logger_name: str,
            handlers: Iterable[logging.Handler] = None,
            universal_log_level=logging.DEBUG,
            with_process_info=False,
            with_thread_info=False
    ):
        """
        Reusable Logger, determined by name
        If parameter `handlers` provided and not None, all previous handlers would be cleared and newly given ones set.
        """
        warnings.warn('Deprecated since 0.2.5. Use NehushtanFileLogger instead!', DeprecationWarning)

        self.with_process_info = with_process_info
        self.with_thread_info = with_thread_info
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(universal_log_level)
        if handlers is not None:
            self.logger.handlers = []
            for handler in handlers:
                # https://docs.python.org/3/library/logging.html#formatter-objects

                format_string = "%(asctime)s <%(name)s> [%(levelname)s]"
                if self.with_process_info:
                    format_string += " <%(process)d:%(processName)s>"
                if self.with_thread_info:
                    format_string += " <%(thread)d:%(threadName)s>"
                format_string += " %(message)s | %(json_string)s"

                handler.setFormatter(
                    logging.Formatter(format_string)
                )
                self.logger.addHandler(handler)

    def debug(self, message: str, extra=None):
        self.logger.debug(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    def info(self, message: str, extra=None):
        self.logger.info(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    def warning(self, message: str, extra=None):
        self.logger.warning(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    def error(self, message: str, extra=None):
        self.logger.error(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    def exception(self, message: str, exception: BaseException):
        """
        Since version 1.2 彭启航之野望
        :param message:
        :param exception:
        :return:
        """
        self.logger.exception(
            msg=message,
            extra=self.ensure_extra_as_dict(exception.__str__()),
            stack_info=True,
        )

    def critical(self, message: str, extra=None):
        self.logger.critical(
            msg=message,
            extra=self.ensure_extra_as_dict(extra)
        )

    @staticmethod
    def make_silent_handler():
        s_handler = logging.NullHandler()
        return s_handler

    @staticmethod
    def make_stdout_handler(logger_level=logging.DEBUG):
        s_handler = logging.StreamHandler(stream=sys.stdout)
        s_handler.setLevel(logger_level)
        return s_handler

    @staticmethod
    def make_stderr_handler(logger_level=logging.WARN):
        s_handler = logging.StreamHandler(stream=sys.stderr)
        s_handler.setLevel(logger_level)
        return s_handler

    @staticmethod
    def make_timed_rotating_file_handler(file_name='shovel.log', logger_level=logging.DEBUG, backup_count=7):
        rf_handler = logging.handlers.TimedRotatingFileHandler(
            filename=file_name,
            when='midnight',
            interval=1,
            backupCount=backup_count
        )
        rf_handler.setLevel(logger_level)
        return rf_handler

    @staticmethod
    def make_fixed_file_handler(file_name='shovel.log', logger_level=logging.DEBUG):
        f_handler = logging.FileHandler(file_name)
        f_handler.setLevel(logger_level)
        return f_handler

    def ensure_extra_as_dict(self, extra):
        """
        Since 0.1.16, add ensure_ascii as False to allow unicode chars
        """
        return {
            "json_string": json.dumps(extra, default=lambda inner_x: inner_x.__str__(), ensure_ascii=False),
        }

    @staticmethod
    def get_silent_logger(logger_name: str):
        return NehushtanLogger(
            logger_name=logger_name,
            handlers=[NehushtanLogger.make_silent_handler()]
        )
