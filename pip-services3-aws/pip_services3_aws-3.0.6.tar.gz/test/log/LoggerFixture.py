# -*- coding: utf-8 -*-
import time

from pip_services3_components.log import CachedLogger, LogLevel


class LoggerFixture:
    _logger: CachedLogger = None

    def __init__(self, logger: CachedLogger):
        self._logger = logger

    def test_log_level(self):
        assert self._logger.get_level() >= LogLevel.Nothing
        assert self._logger.get_level() <= LogLevel.Trace

    def test_simple_logging(self):
        self._logger.set_level(LogLevel.Trace)

        self._logger.fatal(None, None, "Fatal error message")
        self._logger.error(None, None, "Error message")
        self._logger.warn(None, "Warning message")
        self._logger.info(None, "Information message")
        self._logger.debug(None, "Debug message")
        self._logger.trace(None, "Trace message")

        self._logger.dump()

        time.sleep(1)

    def test_error_logging(self):
        try:
            # Raise an exception
            raise Exception()
        except Exception as e:
            self._logger.fatal("123", e, "Fatal error")
            self._logger.error("123", e, "Recoverable error")

        self._logger.dump()

        time.sleep(1)
