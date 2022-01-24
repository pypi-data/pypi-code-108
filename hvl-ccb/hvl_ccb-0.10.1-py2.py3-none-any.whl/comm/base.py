#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Module with base classes for communication protocols.
"""

import logging
from abc import ABC, abstractmethod
from threading import RLock
from time import sleep
from typing import Type, Optional

from ..configuration import ConfigurationMixin, EmptyConfig, configdataclass
from ..utils.typing import Number
from hvl_ccb.exception import CCBException

logger = logging.getLogger(__name__)


class CommunicationException(CCBException):
    pass


class CommunicationProtocol(ConfigurationMixin, ABC):
    """
    Communication protocol abstract base class.

    Specifies the methods to implement for communication protocol, as well as
    implements some default settings and checks.
    """

    def __init__(self, config) -> None:
        """
        Constructor for CommunicationProtocol. Takes a configuration dict or
        configdataclass as the single parameter.

        :param config: Configdataclass or dictionary to be used with the default
            config dataclass.
        """

        super().__init__(config)

        #: Access lock to use with context manager when
        #: accessing the communication protocol (thread safety)
        self.access_lock = RLock()

    # TECH: to be uncommented; pending for v1.0
    # @property
    # @abstractmethod
    # def is_open(self) -> Optional[bool]:
    #     pass  # pragma: no cover

    @abstractmethod
    def open(self):
        """
        Open communication protocol
        """
        pass  # pragma: no cover

    @abstractmethod
    def close(self):
        """
        Close the communication protocol
        """
        pass  # pragma: no cover

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class NullCommunicationProtocol(CommunicationProtocol):
    """
    Communication protocol that does nothing.
    """

    def open(self) -> None:
        """
        Void open function.
        """
        pass

    def close(self) -> None:
        """
        Void close function.
        """
        pass

    @staticmethod
    def config_cls() -> Type[EmptyConfig]:
        """
        Empty configuration

        :return: EmptyConfig
        """
        return EmptyConfig


@configdataclass
class AsyncCommunicationProtocolConfig:
    """
    Base configuration data class for asynchronous communication protocols
    """

    #: The terminator character. Typically this is ``b'\r\n'`` or ``b'\n'``, but can
    #: also be ``b'\r'`` or other combinations. This defines the end of a single line.
    terminator: bytes = b"\r\n"

    #: Standard encoding of the connection. Typically this is ``utf-8``, but can also
    #: be ``latin-1`` or something from here:
    #: https://docs.python.org/3/library/codecs.html#standard-encodings
    encoding: str = "utf-8"
    #: Encoding error handling scheme as defined here:
    #: https://docs.python.org/3/library/codecs.html#error-handlers
    #: By default strict error handling that raises `UnicodeError`.
    encoding_error_handling: str = "strict"

    #: time to wait between attempts of reading a non-empty text
    wait_sec_read_text_nonempty: Number = 0.5

    #: default number of attempts to read a non-empty text
    default_n_attempts_read_text_nonempty: int = 10

    def clean_values(self):

        try:
            "".encode(encoding=self.encoding)
        except LookupError as e:
            raise ValueError(str(e))

        try:
            "\uFFFD".encode(encoding="ascii", errors=self.encoding_error_handling)
        except LookupError as e:
            raise ValueError(str(e))
        except UnicodeEncodeError:
            # expected error
            pass

        if self.wait_sec_read_text_nonempty <= 0:
            raise ValueError(
                "Wait time between attempts to read a non-empty text must be be a "
                "positive value (in seconds)."
            )

        if self.default_n_attempts_read_text_nonempty <= 0:
            raise ValueError(
                "Default number of attempts of reading a non-empty text must be a "
                "positive integer."
            )


class AsyncCommunicationProtocol(CommunicationProtocol):
    """
    Abstract base class for asynchronous communication protocols
    """

    @staticmethod
    def config_cls() -> Type[AsyncCommunicationProtocolConfig]:
        return AsyncCommunicationProtocolConfig

    @abstractmethod
    def read_bytes(self) -> bytes:
        """
        Read a single line as `bytes` from the communication.

        This method uses `self.access_lock` to ensure thread-safety.

        :return: a single line as `bytes` containing the terminator, which can also be
            empty b""
        """
        pass  # pragma: no cover

    @abstractmethod
    def write_bytes(self, data: bytes) -> int:
        """
        Write data as `bytes` to the communication.

        This method uses `self.access_lock` to ensure thread-safety.

        :param data: data as `bytes`-string to be written
        :return: number of bytes written
        """
        pass  # pragma: no cover

    def read(
        self,
    ) -> str:
        """
        Read a single line of text as `str` from the communication.

        :return: text as `str` including the terminator, which can also be empty ""
        """
        return self.read_bytes().decode(
            encoding=self.config.encoding, errors=self.config.encoding_error_handling
        )

    def write(
        self,
        text: str,
    ):
        """
        Write text as `str` to the communication.

        :param text: test as a `str` to be written
        """
        self.write_bytes(
            text.encode(
                encoding=self.config.encoding,
                errors=self.config.encoding_error_handling,
            )
            + self.config.terminator
        )

    def read_nonempty(
        self,
        n_attempts_max: Optional[int] = None,
        attempt_interval_sec: Optional[Number] = None,
    ) -> Optional[str]:
        """
        Try to read a non-empty single line of text as `str` from the communication.
        If the host does not reply or reply with white space only, it will return None.

        :return: a non-empty text as a `str` or `None` in case of an empty string
        :param n_attempts_max: Amount of attempts how often a non-empty text is tried to
            be read
        :param attempt_interval_sec: time between the reading attempts
        """
        if n_attempts_max is None:
            n_attempts_max = self.config.default_n_attempts_read_text_nonempty
        if attempt_interval_sec is None:
            attempt_interval_sec = self.config.wait_sec_read_text_nonempty

        answer = self.read().strip()

        while len(answer) == 0 and n_attempts_max > 0:
            sleep(attempt_interval_sec)
            answer = self.read().strip()
            n_attempts_max -= 1
        if answer == "":
            return None  # Return None for an empty String
        return answer

    def read_all(
        self,
        n_attempts_max: Optional[int] = None,
        attempt_interval_sec: Optional[Number] = None,
    ) -> Optional[str]:
        """
        Read all lines of text from the connection till nothing is left to read.

        :param n_attempts_max: Amount of attempts how often a non-empty text is tried to
            be read
        :param attempt_interval_sec: time between the reading attempts
        :return: A multi-line `str` including the terminator internally
        """

        answer = self.read_nonempty(
            n_attempts_max=n_attempts_max,
            attempt_interval_sec=attempt_interval_sec,
        )
        result = ""
        newline = self.config.terminator.decode(
            encoding=self.config.encoding, errors=self.config.encoding_error_handling
        )
        while answer:
            result = f"{result}{newline}{answer}"
            answer = self.read_nonempty(
                n_attempts_max=n_attempts_max,
                attempt_interval_sec=attempt_interval_sec,
            )

        if result == "":
            return None
        return f"{result.strip()}{self.config.terminator}"

    def read_text(self) -> str:
        """
        Read one line of text from the serial port. The input buffer may
        hold additional data afterwards, since only one line is read.

        NOTE: backward-compatibility proxy for `read` method; to be removed in v1.0

        :return: String read from the serial port; `''` if there was nothing to read.
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        return self.read()

    def write_text(self, text: str):
        """
        Write text to the serial port. The text is encoded and terminated by
        the configured terminator.

        NOTE: backward-compatibility proxy for `read` method; to be removed in v1.0

        :param text: Text to send to the port.
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        return self.write(text)

    def read_text_nonempty(
        self,
        n_attempts_max: Optional[int] = None,
        attempt_interval_sec: Optional[Number] = None,
    ) -> Optional[str]:
        """
        Reads from the serial port, until a non-empty line is found, or the number of
        attempts is exceeded.

        NOTE: backward-compatibility proxy for `read` method; to be removed in v1.0

        Attention: in contrast to `read_text`, the returned answer will be stripped of
        a whitespace newline terminator at the end, if such terminator is set in
        the initial configuration (default).

        :param n_attempts_max: maximum number of read attempts
        :param attempt_interval_sec: time between the reading attempts
        :return: String read from the serial port; `''` if number of attempts is
            exceeded or serial port is not opened.
        """
        return self.read_nonempty(
            n_attempts_max=n_attempts_max,
            attempt_interval_sec=attempt_interval_sec,
        )


class SyncCommunicationProtocolConfig(AsyncCommunicationProtocolConfig):
    pass


class SyncCommunicationProtocol(AsyncCommunicationProtocol, ABC):
    """
    Abstract base class for synchronous communication protocols with `query()`
    """

    @staticmethod
    def config_cls() -> Type[SyncCommunicationProtocolConfig]:
        return SyncCommunicationProtocolConfig

    def query(self, command: str) -> Optional[str]:
        """
        Send a command to the interface and handle the status message.
        Eventually raises an exception.

        :param command: Command to send
        :return: Answer from the interface, which can be None instead of an empty reply
        """

        with self.access_lock:
            self.write(text=command)
            answer: Optional[str] = self.read_text_nonempty()  # expects an answer
            # string or None

            return answer
