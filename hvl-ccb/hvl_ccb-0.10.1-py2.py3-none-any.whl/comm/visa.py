#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Communication protocol for VISA. Makes use of the pyvisa library.
The backend can be NI-Visa or pyvisa-py.

Information on how to install a VISA backend can be found here:
https://pyvisa.readthedocs.io/en/master/getting_nivisa.html

So far only TCPIP SOCKET and TCPIP INSTR interfaces are supported.
"""

import logging
from ipaddress import IPv4Address, IPv6Address
from time import sleep
from typing import Tuple, Union, Type, Optional, cast

import pyvisa as visa
from pyvisa.resources import MessageBasedResource
from pyvisa_py.protocols.rpc import RPCError  # type: ignore

from hvl_ccb.utils.enum import AutoNumberNameEnum
from hvl_ccb.utils.validation import validate_and_resolve_host, validate_tcp_port
from .base import CommunicationProtocol, CommunicationException
from ..configuration import configdataclass

logger = logging.getLogger(__name__)


class VisaCommunicationError(IOError, CommunicationException):
    """
    Base class for VisaCommunication errors.
    """

    pass


@configdataclass
class VisaCommunicationConfig:
    """
    `VisaCommunication` configuration dataclass.
    """

    class InterfaceType(AutoNumberNameEnum, init="value"):  # type:ignore
        """
        Supported VISA Interface types.
        """

        #: VISA-RAW protocol
        TCPIP_SOCKET = ((),)

        #: VXI-11 protocol
        TCPIP_INSTR = ((),)

        def address(self, host: str, port: int = None, board: int = None) -> str:
            """
            Address string specific to the VISA interface type.

            :param host: host IP address
            :param port: optional TCP port
            :param board: optional board number
            :return: address string
            """

            if self.name == VisaCommunicationConfig.InterfaceType.TCPIP_SOCKET:
                return f"TCPIP{board}::{host}::{port}::SOCKET"
            elif self.name == VisaCommunicationConfig.InterfaceType.TCPIP_INSTR:
                return f"TCPIP::{host}::INSTR"
            else:
                assert False, self.name + " is unkonow InterfaceType."

    # IP address of the VISA device.
    host: Union[str, IPv4Address, IPv6Address]

    #: Interface type of the VISA connection, being one of :class:`InterfaceType`.
    interface_type: Union[str, InterfaceType]

    #: Board number is typically 0 and comes from old bus systems.
    board: int = 0

    #: TCP port, standard is 5025.
    port: int = 5025

    #: Timeout for commands in milli seconds.
    timeout: int = 5000

    #: Chunk size is the allocated memory for read operations. The standard is 20kB,
    #: and is increased per default here to 200kB. It is specified in bytes.
    chunk_size: int = 204800

    #: Timeout for opening the connection, in milli seconds.
    open_timeout: int = 1000

    #: Write termination character.
    write_termination: str = "\n"

    #: Read termination character.
    read_termination: str = "\n"

    visa_backend: str = ""
    """
    Specifies the path to the library to be used with PyVISA as a backend. Defaults
    to None, which is NI-VISA (if installed), or pyvisa-py (if NI-VISA is not found).
    To force the use of pyvisa-py, specify '@py' here.
    """

    def clean_values(self):
        # in principle, host is allowed to be IP or FQDN. However, we only allow IP:
        self.force_value("host", validate_and_resolve_host(self.host, logger))
        validate_tcp_port(self.port, logger)

        if not isinstance(self.interface_type, self.InterfaceType):
            self.force_value("interface_type", self.InterfaceType(self.interface_type))

        if self.board < 0:
            raise ValueError("Board number has to be >= 0.")

        if self.timeout < 0:
            raise ValueError("Timeout has to be >= 0.")

        if self.open_timeout < 0:
            raise ValueError("Open Timeout has to be >= 0.")

        allowed_terminators = ("\n", "\r", "\r\n")
        if self.read_termination not in allowed_terminators:
            raise ValueError("Read terminator has to be \\n, \\r or \\r\\n.")

        if self.write_termination not in allowed_terminators:
            raise ValueError("Write terminator has to be \\n, \\r or \\r\\n.")

    @property
    def address(self) -> str:
        """
        Address string depending on the VISA protocol's configuration.

        :return: address string corresponding to current configuration
        """

        return self.interface_type.address(  # type: ignore
            cast(str, self.host),
            port=self.port,
            board=self.board,
        )


class VisaCommunication(CommunicationProtocol):
    """
    Implements the Communication Protocol for VISA / SCPI.
    """

    #: The maximum of commands that can be sent in one round is 5 according to the
    #: VISA standard.
    MULTI_COMMANDS_MAX = 5

    #: The character to separate two commands is ; according to the VISA standard.
    MULTI_COMMANDS_SEPARATOR = ";"

    #: Small pause in seconds to wait after write operations, allowing devices to
    #: really do what we tell them before continuing with further tasks.
    WAIT_AFTER_WRITE = 0.08  # seconds to wait after a write is sent

    def __init__(self, configuration):
        """
        Constructor for VisaCommunication.
        """

        super().__init__(configuration)

        # create a new resource manager
        if self.config.visa_backend == "":
            self._resource_manager = visa.ResourceManager()
        else:
            self._resource_manager = visa.ResourceManager(self.config.visa_backend)

        self._instrument: Optional[MessageBasedResource] = None

    @staticmethod
    def config_cls() -> Type[VisaCommunicationConfig]:
        return VisaCommunicationConfig

    def open(self) -> None:
        """
        Open the VISA connection and create the resource.
        """

        logger.info("Open the VISA connection.")

        with self.access_lock:
            try:
                self._instrument = cast(
                    MessageBasedResource,
                    self._resource_manager.open_resource(
                        self.config.address,
                        open_timeout=self.config.open_timeout,
                    ),
                )
                self._instrument.chunk_size = self.config.chunk_size
                self._instrument.timeout = self.config.timeout
                self._instrument.write_termination = self.config.write_termination
                self._instrument.read_termination = self.config.read_termination

            except visa.VisaIOError as e:
                logger.error(str(e), exc_info=e)
                if e.error_code != 0:
                    raise VisaCommunicationError from e

            except (
                RPCError,
                ConnectionRefusedError,
                BrokenPipeError,
            ) as e:
                # if pyvisa-py is used as backend, this RPCError can come. As it is
                # difficult to import (hyphen in package name), we "convert" it here to
                # a VisaCommunicationError. Apparently on the Linux runners,
                # a ConnectionRefusedError is raised on fail, rather than an RPCError.
                # On macOS the BrokenPipeError error is raised (from
                # pyvisa-py/protocols/rpc.py:320), with puzzling log message from
                # visa.py: "187 WARNING  Could not close VISA connection, was not
                # started."
                logger.error(str(e), exc_info=e)
                raise VisaCommunicationError from e

            if self._instrument is not None:
                try:
                    # enable keep-alive of the connection. Seems not to work always, but
                    # using the status poller a keepalive of the connection is also
                    # satisfied. Unsupported on RTO 1022 devices.
                    self._instrument.set_visa_attribute(
                        visa.constants.ResourceAttribute.tcpip_keepalive,
                        visa.constants.VI_TRUE,
                    )

                except visa.VisaIOError as e:
                    if e.abbreviation == 'VI_ERROR_NSUP_ATTR':
                        logger.warning(str(e), exc_info=e)
                    else:
                        logger.error(str(e), exc_info=e)
                        if e.error_code != 0:
                            raise VisaCommunicationError from e

    def close(self) -> None:
        """
        Close the VISA connection and invalidates the handle.
        """

        if self._instrument is None:
            logger.warning("Could not close VISA connection, was not started.")
            return

        try:
            with self.access_lock:
                self._instrument.close()
        except visa.InvalidSession as e:
            logger.warning(
                "Could not close VISA connection, session invalid.", exc_info=e
            )

    def write(self, *commands: str) -> None:
        """
        Write commands. No answer is read or expected.

        :param commands: one or more commands to send
        :raises VisaCommunicationError: when connection was not started
        """

        if self._instrument is None:
            msg = "Could not write to VISA connection, was not started."
            logger.error(msg)
            raise VisaCommunicationError(msg)

        with self.access_lock:
            self._instrument.write(self._generate_cmd_string(commands))

        # sleep small amount of time to not overload device
        sleep(self.WAIT_AFTER_WRITE)

    def query(self, *commands: str) -> Union[str, Tuple[str, ...]]:
        """
        A combination of write(message) and read.

        :param commands: list of commands
        :return: list of values
        :raises VisaCommunicationError: when connection was not started, or when trying
            to issue too many commands at once.
        """

        if self._instrument is None:
            msg = "Could not query VISA connection, was not started."
            logger.error(msg)
            raise VisaCommunicationError(msg)

        cmd_string = self._generate_cmd_string(commands)
        with self.access_lock:
            return_string = self._instrument.query(cmd_string)

        if len(commands) == 1:
            return return_string

        return tuple(return_string.split(self.MULTI_COMMANDS_SEPARATOR))

    @classmethod
    def _generate_cmd_string(cls, command_list: Tuple[str, ...]) -> str:
        """
        Generate the command string out of a tuple of strings.

        :param command_list: is the tuple containing multiple commands
        :return: the command string that can be sent via the protocol
        """

        if len(command_list) <= cls.MULTI_COMMANDS_MAX:
            return cls.MULTI_COMMANDS_SEPARATOR.join(command_list)

        raise VisaCommunicationError(
            f"Too many commands at once ({len(command_list)}). Max allowed: "
            f"{cls.MULTI_COMMANDS_MAX}."
        )

    def spoll(self) -> int:
        """
        Execute serial poll on the device. Reads the status byte register STB. This
        is a fast function that can be executed periodically in a polling fashion.

        :return: integer representation of the status byte
        :raises VisaCommunicationError: when connection was not started
        """

        if self._instrument is None:
            msg = "Could not query VISA connection, was not started."
            logger.error(msg)
            raise VisaCommunicationError(msg)

        interface_type = self.config.interface_type

        if interface_type == VisaCommunicationConfig.InterfaceType.TCPIP_INSTR:
            with self.access_lock:
                stb = self._instrument.read_stb()
            return stb

        if interface_type == VisaCommunicationConfig.InterfaceType.TCPIP_SOCKET:
            return int(self.query("*STB?"))  # type: ignore

        assert False, "Forgot to cover interface_type case?"
