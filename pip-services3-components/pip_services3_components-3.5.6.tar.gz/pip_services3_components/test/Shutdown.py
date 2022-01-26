# -*- coding: utf-8 -*-

import sys
from typing import Any, Optional

from pip_services3_commons.config import ConfigParams, IConfigurable
from pip_services3_commons.errors import ApplicationException
from pip_services3_commons.random import RandomInteger
from pip_services3_commons.run import IOpenable

from .SetInterval import SetInterval


class Shutdown(IConfigurable, IOpenable):
    """
    Random shutdown component that crashes the process
    using various methods.

    The component is usually used for testing, but brave developers
    can try to use it in production to randomly crash microservices.
    It follows the concept of "Chaos Monkey" popularized by Netflix.

     ### Configuration parameters ###

        - mode:          null - crash by NullPointer excepiton, zero - crash by dividing by zero, excetion = crash by unhandled exception, exit - exit the process
        - min_timeout:   minimum crash timeout in milliseconds (default: 5 mins)
        - max_timeout:   maximum crash timeout in milliseconds (default: 15 minutes)

    Example:

        .. code-block:: python
            shutdown = Shutdown()
            shutdown.configure(ConfigParams.from_tuples(
                "mode": "exception"
            ))
            shutdown.shutdown()         # Result: Bang!!! the process crashes

    """
    def __init__(self):
        self.__interval: Any = None
        self.__mode: str = 'exception'
        self.__min_timeout: int = 300000
        self.__max_timeout: int = 900000

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self.__mode = config.get_as_string_with_default('mode', self.__mode)
        self.__min_timeout = config.get_as_integer_with_default('min_timeout', self.__min_timeout)
        self.__max_timeout = config.get_as_integer_with_default('max_timeout', self.__max_timeout)

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self.__interval is not None

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: 	(optional) transaction id to trace execution through call chain.
        """
        if self.__interval is not None:
            self.__interval.stop()

        timeout = RandomInteger.next_integer(self.__min_timeout, self.__max_timeout)
        self.__interval = SetInterval(self.shutdown, timeout)

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: 	(optional) transaction id to trace execution through call chain.
        """
        if self.__interval is not None:
            self.__interval.stop()
            self.__interval = None

    def shutdown(self):
        """
        Crashes the process using the configured crash mode.
        """
        if self.__mode == 'null' or self.__mode == 'nullpointer':
            obj = None
            obj.crash = 123
        elif self.__mode == 'zero' or self.__mode == 'dividebyzero':
            crash = 0 / 100
        elif self.__mode == 'exit' or self.__mode == 'processexit':
            sys.exit(1)
        else:
            err = ApplicationException('test', None, 'CRASH', 'Crash test exception')
            raise err
