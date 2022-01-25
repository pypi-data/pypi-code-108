import abc
from typing import *
from typing import IO


class ScpiTypeBase(object):
    """Base class for SCPI types"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __str__(self) -> str:
        """A textual representation of the object"""
        raise NotImplementedError("Please Implement this method")

    @abc.abstractmethod
    def compose(self) -> str:
        """Converts the given data into SCPI "Device listening" format"""
        raise NotImplementedError("Please Implement this method")

    @classmethod
    @abc.abstractmethod
    def parse(cls, stream: IO):
        """Parses SCPI "Device talking Elements" into an internal representation"""
        raise NotImplementedError("Please Implement this method")


# TypeVar for type hinting subclasses of ScpiTypeBase
ScpiTypes = TypeVar('ScpiTypes', bound=ScpiTypeBase)
