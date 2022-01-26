# Copyright 2020 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import logging.config
import logging.handlers
from sys import stdout, stderr
from cached_property import cached_property


class LoggingConfiguration:
    """
    This class provides an all in one management of all loggers in the stack. By default it pulls existing loggers,
    stores additional ones along with handlers and formatters.
    """

    default_fmt = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
    default_datefmt = '%Y-%b-%d %H:%M:%S'

    def __init__(self, use_existing_logger=True, log_level=logging.INFO):
        self.blank_formatter = logging.Formatter()
        self.handlers = set()
        if use_existing_logger:
            # retrieve all third party loggers
            self.loggers = dict((name, logger)
                                for name, logger in logging.root.manager.loggerDict.items()
                                if isinstance(logger, logging.Logger))
        else:
            self.loggers = {}
        self._log_level = log_level

    @cached_property
    def formatter(self):
        return self.default_formatter

    @cached_property
    def default_formatter(self):
        return logging.Formatter(
            fmt=self.default_fmt,
            datefmt=self.default_datefmt
        )

    def get_logger(self, name, level=logging.NOTSET):
        """
        Return a logging.Logger object with formatters and handlers added.
        :param name: Name to assign to the logger (usually __name__)
        :param int level: Log level to assign to the logger upon creation
        """
        if name in self.loggers:
            logger = self.loggers[name]
        else:
            logger = logging.getLogger(name)
            self.loggers[name] = logger

        logger.setLevel(level or self._log_level)
        for h in self.handlers:
            logger.addHandler(h)

        return logger

    def add_handler(self, handler, level=logging.NOTSET):
        """
        Add a created handler, set its format/level if needed and register all loggers to it
        :param logging.Handler handler:
        :param int level: Log level to assign to the created handler
        """
        handler.setLevel(level or self._log_level)
        handler.setFormatter(self.formatter)
        for name in self.loggers:
            self.loggers[name].addHandler(handler)
        self.handlers.add(handler)

    def add_stdout_handler(self, level=None):
        self.add_handler(logging.StreamHandler(stdout), level=level or self._log_level)

    def add_stderr_handler(self, level=None):
        self.add_handler(logging.StreamHandler(stderr), level=level or self._log_level)

    def add_file_handler(self, filename, level=None):
        self.add_handler(logging.FileHandler(filename=filename), level=level or self._log_level)

    def set_log_level(self, level):
        self._log_level = level
        for h in self.handlers:
            h.setLevel(self._log_level)
        for name in self.loggers:
            self.loggers[name].setLevel(self._log_level)

    def set_formatter(self, formatter):
        """
        Set all handlers to use formatter
        :param logging.Formatter formatter:
        """
        self.__dict__['formatter'] = formatter
        for h in self.handlers:
            h.setFormatter(self.formatter)

    def reset(self):
        """Remove all handlers of existing logger"""
        for l in self.loggers.values():
            while l.handlers:
                l.removeHandler(l.handlers[0])

        while self.handlers:
            h = self.handlers.pop()
            del h


# A logging configuration singleton that will be the only source of logger
logging_config = LoggingConfiguration()


class AppLogger:
    """
    Mixin class for logging. An object subclassing this can log using its class name. Contains a
    logging.Logger object and exposes its log methods.
    """
    log_cfg = logging_config

    def debug(self, msg, *args):
        self._logger.debug(msg, *args)

    def info(self, msg, *args):
        self._logger.info(msg, *args)

    def warning(self, msg, *args):
        self._logger.warning(msg, *args)

    def error(self, msg, *args):
        self._logger.error(msg, *args)

    def critical(self, msg, *args):
        self._logger.critical(msg, *args)

    @cached_property
    def _logger(self):
        return self.log_cfg.get_logger(self.__class__.__name__)