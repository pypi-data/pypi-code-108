# -*- coding: utf-8 -*-
import time

from pip_services3_components.log import CachedLogger, LogLevel


class LoggerFixture:
    _logger: CachedLogger

    def __init__(self, logger: CachedLogger):
        self._logger = logger

    def test_log_level(self):
        assert self._logger.get_level() >= LogLevel.Nothing
        assert self._logger.get_level() <= LogLevel.Trace

    def test_simple_logging(self):
        self._logger.set_level(LogLevel.Trace)

        self._logger.fatal("987", None, "Fatal error message")
        self._logger.error("987", None, "Error message")
        self._logger.warn("987", "Warning message")
        self._logger.info("987", "Information message")
        self._logger.debug("987", "Debug message")
        self._logger.trace("987", "Trace message")

        self._logger.dump()

        # time.sleep(1)

    def test_error_logging(self):
        try:
            # Raise an exception
            raise Exception('Test error exception')
        except Exception as err:
            self._logger.fatal("123", err, "Fatal error")
            self._logger.error("123", err, "Recoverable error")

        self._logger.dump()

        # time.sleep(1)
