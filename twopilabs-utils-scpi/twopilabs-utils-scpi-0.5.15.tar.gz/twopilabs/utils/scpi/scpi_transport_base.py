import abc
from typing import *
from typing import IO, BinaryIO
from io import UnsupportedOperation
import logging

class ScpiTransportBase(IO):
    # attribute default values
    _transport_class: str = 'Unknown'
    _transport_info: str = 'Unknown'
    _transport_type: str = 'Unknown'

    _encoding: str = 'utf8'
    _newline: str = '\r\n'

    _io: BinaryIO = None
    _logger: logging.Logger

    @classmethod
    @abc.abstractmethod
    def discover(cls, **kwargs):
        """Discovers a list of devices available on the system on the corresponding transport"""
        raise NotImplementedError("Please implement this method")

    @classmethod
    @abc.abstractmethod
    def from_resource_name(cls, resource_name):
        """Converts a VISA resource name into an address object that can be used to open a transport"""
        raise NotImplementedError("Please implement this method")

    @classmethod
    @abc.abstractmethod
    def to_resource_name(cls, resource):
        """Converts an existing resource into its VISA resource name representation"""
        raise NotImplementedError("Please implement this method")

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__()

    @property
    def transport_class(self):
        return self._transport_class

    @property
    def transport_info(self):
        return self._transport_info

    @property
    def transport_type(self):
        return self._transport_type

    def read(self, n: int = -1) -> Union[bytes, bytearray]:
        self._logger.debug(f'read: block with size of {n} bytes')
        return self._io.read(n)

    def write(self, s: Union[bytes, bytearray]) -> int:
        n = self._io.write(s)
        self._io.flush()
        self._logger.debug(f'write: block with size of {n} bytes')
        return n

    def readline(self, size: int = -1) -> str:
        data = self._io.readline(size)
        self._logger.debug(f'read line {str(bytes(data))[1:]}')
        return data.decode(self._encoding).rstrip(self._newline)

    def writeline(self, line: str) -> None:
        data = (line + self._newline).encode(self._encoding)
        self._logger.debug(f'write line {str(bytes(data))[1:]}')
        self._io.writelines([data])
        self._io.flush()

    def readlines(self, hint: int = ...) -> List[AnyStr]:
        raise UnsupportedOperation

    def writelines(self, lines: Iterable[AnyStr]) -> None:
        raise UnsupportedOperation

    def close(self) -> None:
        self._io.close()

    @property
    def closed(self) -> bool:
        return self._io.closed

    @property
    def mode(self) -> str:
        return self._io.mode

    @property
    def name(self) -> str:
        return self._io.name

    def isatty(self) -> bool:
        return self._io.isatty()

    def fileno(self) -> int:
        return self._io.fileno()

    def flush(self) -> None:
        return self._io.flush()

    def readable(self) -> bool:
        return self._io.readable()

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._io.seek(offset, whence)

    def seekable(self) -> bool:
        return self._io.seekable()

    def tell(self) -> int:
        return self._io.tell()

    def truncate(self, size: Optional[int] = ...) -> int:
        return self._io.truncate(size)

    def writable(self) -> bool:
        return self._io.writable()

    def __next__(self) -> AnyStr:
        return self._io.__next__()

    def __iter__(self) -> Iterator[AnyStr]:
        return self._io.__iter__()

    def __enter__(self) -> IO[AnyStr]:
        return self._io.__enter__()

    def __exit__(self, t: Optional[Type[BaseException]], value: Optional[BaseException],
                 traceback) -> Optional[bool]:
        return self._io.__exit__(t, value, traceback)

    def __del__(self):
        if self._io is not None:
            del self._io
        del self._logger

# TypeVar for type hinting subclasses of ScpiTransportBase
ScpiTransports = TypeVar('ScpiTransports', bound=ScpiTransportBase)
