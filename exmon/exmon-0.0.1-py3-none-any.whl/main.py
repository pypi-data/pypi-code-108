import logging
import sys
from types import TracebackType
from typing import List, Type, Union

from exmon.alarm import Alarm
from exmon.exceptions import ServiceExcpetion
from exmon.services import Service
from exmon.logging import DefaultFormatter


class ExMon:
    """ Modular Exception Monitoring Tool """

    def __init__(
        self,
        logger: logging.Logger = None,
        log_level: Union[int, str] = logging.DEBUG,
        services: List[Service] = None
    ):

        # list of services
        if services is None:
            self.services = []
        else:
            self.services = services

        # configure logging
        if logger is None:
            # default logging
            self.logging()
        else:
            self._logger = logger
            self._logger.setLevel(log_level)

        # wrap default excepthook
        self.wrap_excepthook()

    def wrap_excepthook(self):
        """Saves the orgiginal excepthook
        and replaces it with a new custom one. """

        # save original/default excepthook
        self.existing_except_hook = sys.excepthook

        # set custom excepthook to fire when exceptions occure
        sys.excepthook = self.excepthook

    def excepthook(
        self,
        exc_type: Type[BaseException],
        exc: BaseException,
        exc_traceback: TracebackType
    ) -> Alarm:
        """Custom excepthook. Fires every time an exception occurs.

        Args:
            exc_type (:obj:`Type[BaseException]`): type of exception, that was thrown
            exc (:obj:`BaseException`): exception instance, that was thrown
            exc_traceback (:obj:`TracebackType`): traceback, that led to the exception

        Returns:
            :obj:`ExceptionData`: holds information about thrown exception
        """

        # create exception data wrapper
        data = Alarm(exc_type, exc, exc_traceback)

        # send exception to registered services
        for service in self.services:
            try:
                service(data)
                self._logger.debug(f'Send alert to {str(service)}')
            except ServiceExcpetion as sexc:
                self._logger.error(sexc)

        # call original/default except hook that was saved before
        self.existing_except_hook(exc_type, exc, exc_traceback)

        return data

    def add_service(self, service: Service) -> None:
        """Binds a new service, that will be called every time an exception occurs

        Args:
            service (:obj:`Service`): Service that will be added.
        """
        self.services.append(service)

    def logging(self):
        """Configures default logging"""

        # create logger and set logging level
        self._logger = logging.getLogger('exmon.logging')
        self._logger.setLevel(logging.DEBUG)

        # create handler that prints to console
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(DefaultFormatter())

        # add handler to default logger
        self._logger.addHandler(handler)

    def test_logging(self) -> None:
        """tests logging output"""
        self._logger.debug('This is the debug logger')
        self._logger.info('This is the info logger')
        self._logger.warning('This is the warn logger')
        self._logger.error('This is the error logger')
        self._logger.critical('This is the critical logger')
