import logging
import os
import struct
import sys
import time
from abc import ABC, abstractmethod
from typing import Any, Dict

from .libc import sysctl

logger = logging.getLogger(__name__)


class Variable(ABC):
    """
    A user defines a variable with its "name" and a way to fetch its value.
    """

    def __init__(self, name: str, params: Dict):
        assert name
        self._name = name
        self._value = None
        self._last_value = None

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other) -> bool:
        return self._name == other._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Any:
        return self._value

    @property
    def last_value(self) -> Any:
        return self._last_value

    def new_value(self) -> Any:
        self._last_value = self._value
        self._value = self._fetch_value()
        return self._value

    @abstractmethod
    def _fetch_value(self) -> Any:
        return self._value


class SyscmdVariable(Variable):
    """
    A user defines a variable with its "name" and sysctl name for its value.
    """

    def __init__(self, name: str, params: Dict):
        super().__init__(name, params)

        self._cmd = params["syscmd"]
        self._last_value = self._value = self._fetch_value()

    def _fetch_value(self) -> Any:
        return os.popen(self._cmd).read().strip()


class SysctlVariable(Variable):
    """
    A user defines a variable with its "name" and sysctl name for its value.
    """

    def __init__(self, name: str, params: Dict):
        super().__init__(name, params)

        self._sysctl_name = params["sysctl"]
        self._sysctl = sysctl.Sysctl(self._sysctl_name)
        self._last_value = self._value = self._sysctl.value

    def _fetch_value(self) -> Any:
        return self._sysctl.value


def instantiate_variable(name: str, params: Dict) -> Any:
    assert name

    if "sysctl" in params:
        return SysctlVariable(name, params)
    elif "syscmd" in params:
        return SyscmdVariable(name, params)
    else:
        raise Exception("Unknown variable type")
