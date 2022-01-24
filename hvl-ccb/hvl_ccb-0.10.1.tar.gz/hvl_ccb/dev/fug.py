#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device classes for "Probus V - ADDAT30" Interfaces which are used to control power
supplies from FuG Elektronik GmbH

This interface is used for many FuG power units.
Manufacturer homepage:
https://www.fug-elektronik.de

The Professional Series of Power Supplies from FuG is a series of low, medium and high
voltage direct current power supplies as well as capacitor chargers.
The class FuG is tested with a HCK 800-20 000 in Standard Mode.
The addressable mode is not implemented.
Check the code carefully before using it with other devices.
Manufacturer homepage:
https://www.fug-elektronik.de/netzgeraete/professional-series/

The documentation of the interface from the manufacturer can be found here:
https://www.fug-elektronik.de/wp-content/uploads/download/de/SOFTWARE/Probus_V.zip

The provided classes support the basic and some advanced commands.
The commands for calibrating the power supplies are not implemented, as they are only
for very special porpoises and
should not used by "normal" customers.
"""

import logging
import re
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Union, cast, Optional

from .base import SingleCommDevice, DeviceException
from ..comm import SerialCommunication, SerialCommunicationConfig
from ..comm.serial import (
    SerialCommunicationParity,
    SerialCommunicationStopbits,
    SerialCommunicationBytesize,
)
from ..configuration import configdataclass
from ..utils.enum import NameEnum
from ..utils.typing import Number

logger = logging.getLogger(__name__)


class FuGErrorcodes(NameEnum, init="description possible_reason"):  # type:ignore
    """
    The power supply can return an errorcode. These errorcodes are handled by this
    class. The original errorcodes from the source are with one or two digits,
    see documentation of Probus V chapter 5.
    All three-digit errorcodes are from this python module.
    """

    E0 = "no error", "standard response on each command"
    E1 = (
        "no data available",
        "Customer tried to read from GPIB but there were no data prepared. "
        "(IBIG50 sent command ~T2 to ADDA)",
    )
    E2 = "unknown register type", "No valid register type after '>'"
    E4 = (
        "invalid argument",
        "The argument of the command was rejected .i.e. malformed number",
    )
    E5 = "argument out of range", "i.e. setvalue higher than type value"
    E6 = (
        "register is read only",
        "Some registers can only be read but not written to. (i.e. monitor registers)",
    )
    E7 = "Receive Overflow", "Command string was longer than 50 characters."
    E8 = (
        "EEPROM is write protected",
        "Write attempt to calibration data while the write protection switch was set "
        "to write protected.",
    )
    E9 = (
        "address error",
        "A non addressed command was sent to ADDA while it was in addressable mode "
        "(and vice versa).",
    )
    E10 = "unknown SCPI command", "This SCPI command is not implemented"
    E11 = (
        "not allowed Trigger-on-Talk",
        "Not allowed attempt to Trigger-on-Talk (~T1) while ADDA was in addressable "
        "mode.",
    )
    E12 = "invalid argument in ~Tn command", "Only ~T1 and ~T2 is implemented."
    E13 = (
        "invalid N-value",
        "Register > K8 contained an invalid value. Error code is output on an attempt "
        "to query data with ? or ~T1",
    )
    E14 = "register is write only", "Some registers can only be writte to (i.e.> H0)"
    E15 = "string too long", "i.e.serial number string too long during calibration"
    E16 = (
        "wrong checksum",
        "checksum over command string was not correct, refer also to 4.4 of the "
        "Probus V documentation",
    )
    E100 = (
        "Command is not implemented",
        "You tried to execute a command, which is not implemented or does not exist",
    )
    E106 = (
        "The rampstate is a read-only register",
        "You tried to write data to the register, which can only give "
        "you the status of the ramping.",
    )
    E206 = (
        "This status register is read-only",
        "You tried to write data to this "
        "register, which can only give you "
        "the actual status of the "
        "corresponding digital output.",
    )
    E306 = (
        "The monitor register is read-only",
        "You tried to write data to a "
        "monitor, which can only give you "
        "measured data.",
    )
    E115 = (
        "The given index to select a digital value is out of range",
        "Only integer values between 0 and 1 are allowed.",
    )
    E125 = (
        "The given index to select a ramp mode is out of range",
        "Only integer " "values between 0 and 4 are allowed.",
    )
    E135 = (
        "The given index to select the readback channel is out of range",
        "Only integer values between 0 and 6 are allowed.",
    )
    E145 = (
        "The given value for the AD-conversion is unknown",
        'Valid values for the ad-conversion are integer values from "0" to "7".',
    )
    E155 = (
        "The given value to select a polarity is out range.",
        "The value should be 0 or 1.",
    )
    E165 = "The given index to select the terminator string is out of range", ""
    E504 = "Empty string as response", "The connection is broken."
    E505 = (
        "The returned register is not the requested.",
        "Maybe the connection is overburden.",
    )
    E666 = (
        "You cannot overwrite the most recent error in the interface of the power "
        "supply. But, well: You created an error anyway...",
        "",
    )

    def raise_(self):
        if self is FuGErrorcodes.E0:
            logger.debug('Communication with FuG successful, errorcode "E0" received.')
            return
        logger.debug(f"A FuGError with the errorcode {self.name} was detected.")
        raise FuGError(
            f"{self.description}. Possible reason: {self.possible_reason}",
            errorcode=self.name,
        )


class FuGDigitalVal(IntEnum):
    OFF = 0
    ON = 1
    YES = 1
    NO = 0


class FuGRampModes(IntEnum):
    IMMEDIATELY = 0
    """Standard mode: no ramp"""
    FOLLOWRAMP = 1
    """Follow the ramp up- and downwards"""
    RAMPUPWARDS = 2
    """Follow the ramp only upwards, downwards immediately"""
    SPECIALRAMPUPWARDS = 3
    """Follow a special ramp function only upwards"""
    ONLYUPWARDSOFFTOZERO = 4
    """Follow the ramp up- and downwards, if output is OFF set value is zero"""


class FuGReadbackChannels(IntEnum):
    VOLTAGE = 0
    CURRENT = 1
    STATUSBYTE = 2
    RATEDVOLTAGE = 3
    RATEDCURRENT = 4
    FIRMWARE = 5
    SN = 6


class FuGMonitorModes(IntEnum):
    T256US = 0
    """14 bit + sign, 256 us integration time"""
    T1MS = 1
    """15 bit + sign, 1 ms integration time"""
    T4MS = 2
    """15 bit + sign, 4 ms integration time"""
    T20MS = 3
    """17 bit + sign, 20 ms integration time"""
    T40MS = 4
    """17 bit + sign, 40 ms integration time"""
    T80MS = 5
    """typ. 18 bit + sign, 80 ms integration time"""
    T200MS = 6
    """typ. 19 bit + sign, 200 ms integration time"""
    T800MS = 7
    """typ. 20 bit + sign, 800 ms integration time"""


class FuGPolarities(IntEnum):
    POSITIVE = 0
    NEGATIVE = 1


class FuGTerminators(IntEnum):
    CRLF = 0
    LFCR = 1
    LF = 2
    CR = 3


class FuGProbusIVCommands(NameEnum, init="command input_type"):  # type:ignore
    ID = "*IDN?", None
    RESET = "=", None
    OUTPUT = "F", (FuGDigitalVal, int)
    VOLTAGE = "U", (int, float)
    CURRENT = "I", (int, float)
    READBACKCHANNEL = "N", (FuGReadbackChannels, int)
    QUERY = "?", None
    ADMODE = "S", (FuGMonitorModes, int)
    POLARITY = "P", (FuGPolarities, int)
    XOUTPUTS = "R", int
    """TODO: the possible values are limited to 0..13"""
    EXECUTEONX = "G", (FuGDigitalVal, int)
    """Wait for "X" to execute pending commands"""
    EXECUTE = "X", None
    TERMINATOR = "Y", (FuGTerminators, int)


@configdataclass
class FuGSerialCommunicationConfig(SerialCommunicationConfig):
    #: Baudrate for FuG power supplies is 9600 baud
    baudrate: int = 9600

    #: FuG does not use parity
    parity: Union[str, SerialCommunicationParity] = SerialCommunicationParity.NONE

    #: FuG uses one stop bit
    stopbits: Union[int, SerialCommunicationStopbits] = SerialCommunicationStopbits.ONE

    #: One byte is eight bits long
    bytesize: Union[
        int, SerialCommunicationBytesize
    ] = SerialCommunicationBytesize.EIGHTBITS

    #: The terminator is LF
    terminator: bytes = b"\n"

    #: use 3 seconds timeout as default
    timeout: Number = 3

    #: default time to wait between attempts of reading a non-empty text
    wait_sec_read_text_nonempty: Number = 0.5

    #: default number of attempts to read a non-empty text
    default_n_attempts_read_text_nonempty: int = 10


class FuGSerialCommunication(SerialCommunication):
    """
    Specific communication protocol implementation for
    FuG power supplies.
    Already predefines device-specific protocol parameters in config.
    """

    @staticmethod
    def config_cls():
        return FuGSerialCommunicationConfig

    def query(self, command: str) -> str:
        """
        Send a command to the interface and handle the status message.
        Eventually raises an exception.

        :param command: Command to send
        :raises FuGError: if the connection is broken or the error from the power
            source itself
        :return: Answer from the interface or empty string
        """

        with self.access_lock:
            logger.debug(f"FuG communication, send: {command}")
            self.write_text(command)
            answer: Optional[str] = self.read_text_nonempty()  # expects an answer
            logger.debug(f"FuG communication, receive: {answer}")
            if not answer:
                cast(FuGErrorcodes, FuGErrorcodes.E504).raise_()
            assert answer is not None
            try:
                FuGErrorcodes(answer).raise_()
                return ""
            except ValueError as e:
                logger.error(str(e), exc_info=e)
                if answer.startswith("E"):
                    raise FuGError(f'The unknown errorcode "{answer}" was detected.')
                return answer


@configdataclass
class FuGConfig:
    """
    Device configuration dataclass for FuG power supplies.
    """

    #: Time to wait after subsequent commands during stop (in seconds)
    wait_sec_stop_commands: Number = 0.5

    def clean_values(self):
        if self.wait_sec_stop_commands <= 0:
            raise ValueError(
                "Wait time after subsequent commands during stop must be be a "
                "positive value (in seconds)."
            )


class FuGProbusIV(SingleCommDevice, ABC):
    """
    FuG Probus IV device class

    Sends basic SCPI commands and reads the answer.
    Only the special commands and PROBUS IV instruction set is implemented.
    """

    def __init__(self, com, dev_config=None):

        # Call superclass constructor
        super().__init__(com, dev_config)

        # Version of the interface (will be retrieved after com is opened)
        self._interface_version = ""

    def __repr__(self):
        return f"FuGProbus({self._interface_version})"

    @staticmethod
    def default_com_cls():
        return FuGSerialCommunication

    @staticmethod
    def config_cls():
        return FuGConfig

    @abstractmethod
    def start(self):
        logger.info("Starting device " + str(self))
        super().start()

        self._interface_version = self.command(FuGProbusIVCommands.ID)
        logger.info(f"Connection to {self._interface_version} established.")

    def stop(self) -> None:
        with self.com.access_lock:
            logger.info(f"Stopping device {self}")
            self.output_off()
            self.reset()
            super().stop()

    def command(self, command: FuGProbusIVCommands, value=None) -> str:
        """

        :param command: one of the commands given within FuGProbusIVCommands
        :param value: an optional value, depending on the command
        :return: a String if a query was performed
        """
        if not (
            (value is None and command.input_type is None)
            or isinstance(value, command.input_type)
        ):
            raise FuGError(
                f"Wrong value for data was given. Expected: "
                f"{command.input_type} and given: {value.__class__}"
            )

        # Differentiate between with and without optional value
        if command.input_type is None:
            return self.com.query(f"{command.command}")
        else:
            return self.com.query(f"{command.command}{value}")

    # Special commands
    def reset(self) -> None:
        """
        Reset of the interface:
        All setvalues are set to zero
        """
        self.command(
            FuGProbusIVCommands.RESET  # type: ignore
        )

    def output_off(self) -> None:
        """
        Switch DC voltage output off.
        """
        self.command(
            FuGProbusIVCommands.OUTPUT,  # type: ignore
            FuGDigitalVal.OFF,
        )


class FuGProbusV(FuGProbusIV):
    """
    FuG Probus V class which uses register based commands to control the power supplies
    """

    def __init__(self, com, dev_config=None):

        # Call superclass constructor
        super().__init__(com, dev_config)

        # Version of the interface (will be retrieved after com is opened)
        # self._interface_version = ""

    def set_register(self, register: str, value: Union[Number, str]) -> None:
        """
        generic method to set value to register

        :param register: the name of the register to set the value
        :param value: which should be written to the register
        """

        self.com.query(f">{register} {value}")

    def get_register(self, register: str) -> str:
        """
        get the value from a register

        :param register: the register from which the value is requested
        :returns: the value of the register as a String
        """

        answer = self.com.query(f">{register} ?").split(":")
        if not answer[0] == register:
            cast(FuGErrorcodes, FuGErrorcodes.E505).raise_()

        return answer[1]


class FuGProbusVRegisterGroups(NameEnum):
    SETVOLTAGE = "S0"
    SETCURRENT = "S1"
    OUTPUTX0 = "B0"
    OUTPUTX1 = "B1"
    OUTPUTX2 = "B2"
    OUTPUTXCMD = "BX"
    OUTPUTONCMD = "BON"
    MONITOR_V = "M0"
    MONITOR_I = "M1"
    INPUT = "D"
    CONFIG = "K"


def _check_for_value_limits(value, max_limit) -> bool:
    if value > max_limit:
        raise FuGError(
            f"The requested value of {value} exceeds the maximal"
            f"technically permissible value of {max_limit}."
        )
    elif value < 0:
        raise ValueError("The value must be positive.")
    return True


class FuGProbusVSetRegisters:
    """
    Setvalue control acc. 4.2.1 for the voltage and the current output
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups):

        self._fug = fug

        _super_register = super_register.value

        self._setvalue: str = _super_register
        self.__max_setvalue: float = 0
        self._actualsetvalue: str = _super_register + "A"
        self._ramprate: str = _super_register + "R"
        self._rampmode: str = _super_register + "B"
        self._rampstate: str = _super_register + "S"
        self._high_resolution: str = _super_register + "H"

    @property
    def _max_setvalue(self) -> float:
        return self.__max_setvalue

    @_max_setvalue.setter
    def _max_setvalue(self, value: Number):
        self.__max_setvalue = float(value)

    @property
    def setvalue(self) -> float:
        """
        For the voltage or current output this setvalue was programmed.

        :return: the programmed setvalue
        """
        return float(self._fug.get_register(self._setvalue))

    @setvalue.setter
    def setvalue(self, value: Number):
        """
        This sets the value for the voltage or current output

        :param value: value in V or A
        """
        _check_for_value_limits(value, self._max_setvalue)
        self._fug.set_register(self._setvalue, value)

    @property
    def actualsetvalue(self) -> float:
        """
        The actual valid set value, which depends on the ramp function.

        :return: actual valid set value
        """
        return float(self._fug.get_register(self._actualsetvalue))

    @actualsetvalue.setter
    def actualsetvalue(self, value: Number):
        _check_for_value_limits(value, self._max_setvalue)
        self._fug.set_register(self._actualsetvalue, value)

    @property
    def ramprate(self) -> float:
        """
        The set ramp rate in V/s.

        :return: ramp rate in V/s
        """
        return float(self._fug.get_register(self._ramprate))

    @ramprate.setter
    def ramprate(self, value: Number):
        """
        The ramp rate can be set in V/s.

        :param value: ramp rate in V/s
        """
        self._fug.set_register(self._ramprate, value)

    @property
    def rampmode(self) -> FuGRampModes:
        """
        The set ramp mode to control the setvalue.

        :return: the mode of the ramp as instance of FuGRampModes
        """
        return FuGRampModes(int(self._fug.get_register(self._rampmode)))

    @rampmode.setter
    def rampmode(self, value: Union[int, FuGRampModes]):
        """
        Sets the ramp mode.

        :param value: index for the ramp mode from FuGRampModes
        :raise FuGError: if a wrong ramp mode is chosen
        """
        try:
            self._fug.set_register(self._rampmode, FuGRampModes(value))
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            cast(FuGErrorcodes, FuGErrorcodes.E125).raise_()

    @property
    def rampstate(self) -> FuGDigitalVal:
        """
        Status of ramp function.

        :return 0: if final setvalue is reached
        :return 1: if still ramping up
        """
        return FuGDigitalVal(int(self._fug.get_register(self._rampstate)))

    @rampstate.setter
    def rampstate(self, _):
        """
        The rampstate is only an output. Writing data to this register will raise an
        exception

        :raise FuGError: if something is written to this attribute
        """
        cast(FuGErrorcodes, FuGErrorcodes.E106).raise_()

    @property
    def high_resolution(self) -> FuGDigitalVal:
        """
        Status of the high resolution mode of the output.

        :return 0: normal operation
        :return 1: High Res. Mode
        """
        return FuGDigitalVal(int(self._fug.get_register(self._high_resolution)))

    @high_resolution.setter
    def high_resolution(self, value: Union[int, FuGDigitalVal]):
        """
        Enables/disables the high resolution mode of the output.

        :param value: FuGDigitalVal
        :raise FuGError: if not a FuGDigitalVal is given
        """
        try:
            if FuGDigitalVal(value) is FuGDigitalVal.ON:
                self._fug.set_register(self._high_resolution, FuGDigitalVal.ON)
            else:
                self._fug.set_register(self._high_resolution, FuGDigitalVal.OFF)
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            cast(FuGErrorcodes, FuGErrorcodes.E115).raise_()


class FuGProbusVDORegisters:
    """
    Digital outputs acc. 4.2.2
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups):

        self._fug = fug

        _super_register = super_register.value

        self._out = _super_register
        self._status = _super_register + "A"

    @property
    def out(self) -> Union[int, FuGDigitalVal]:
        """
        Status of the output according to the last setting. This can differ from the
        actual state if output should only pulse.

        :return: FuGDigitalVal
        """
        return FuGDigitalVal(int(self._fug.get_register(self._out)))

    @out.setter
    def out(self, value: Union[int, FuGDigitalVal]):
        """
        Set the output ON or OFF. If pulsing is enabled, it only pulses.

        :param value: FuGDigitalVal
        :raise FuGError: if a non FuGDigitalVal is given
        """
        try:
            if FuGDigitalVal(value) is FuGDigitalVal.ON:
                self._fug.set_register(self._out, FuGDigitalVal.ON)
            else:
                self._fug.set_register(self._out, FuGDigitalVal.OFF)
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            FuGErrorcodes("E115").raise_()

    @property
    def status(self) -> FuGDigitalVal:
        """
        Returns the actual value of output. This can differ from the set value if
        pulse function is used.

        :return: FuGDigitalVal
        """
        return FuGDigitalVal(int(self._fug.get_register(self._status)))

    @status.setter
    def status(self, _):
        """
        The status is only an output. Writing data to this register will raise an
        exception

        :raise FuGError: read only
        """
        FuGErrorcodes("E206").raise_()


class FuGProbusVMonitorRegisters:
    """
    Analog monitors acc. 4.2.3
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups):

        self._fug = fug
        _super_register = super_register.value

        self._value = _super_register
        self._value_raw = _super_register + "R"
        self._adc_mode = _super_register + "I"

    @property
    def value(self) -> float:
        """
        Value from the monitor.

        :return: a float value in V or A
        """
        return float(self._fug.get_register(self._value))

    @value.setter
    def value(self, _):
        """
        Monitor is read-only!

        :raise FuGError: read-only
        """
        FuGErrorcodes("E306").raise_()

    @property
    def value_raw(self) -> float:
        """
        uncalibrated raw value from AD converter

        :return: float value from ADC
        """
        return float(self._fug.get_register(self._value_raw))

    @value_raw.setter
    def value_raw(self, _):
        """
        Monitor is read-only!

        :raise FuGError: read-only
        """
        FuGErrorcodes("E306").raise_()

    @property
    def adc_mode(self) -> FuGMonitorModes:
        """
        The programmed resolution and integration time of the AD converter

        :return: FuGMonitorModes
        """
        return FuGMonitorModes(int(self._fug.get_register(self._adc_mode)))

    @adc_mode.setter
    def adc_mode(self, value: Union[int, FuGMonitorModes]):
        """
        Sets the resolution and integration time of the AD converter with the given
        settings in FuGMonitorModes.

        :param value: index of the monitor mode from FuGMonitorModes
        :raise FuGError: if index is not in FuGMonitorModes
        """
        try:
            self._fug.set_register(self._adc_mode, FuGMonitorModes(value))
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            raise FuGErrorcodes("E145").raise_()


class FuGProbusVDIRegisters:
    """
    Digital Inputs acc. 4.2.4
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups):

        self._fug = fug

        _super_register = super_register.value

        self._cv_mode = _super_register + "VR"
        self._cc_mode = _super_register + "IR"
        self._reg_3 = _super_register + "3R"
        self._x_stat = _super_register + "X"
        self._on = _super_register + "ON"
        self._digital_control = _super_register + "SD"
        self._analog_control = _super_register + "SA"
        self._calibration_mode = _super_register + "CAL"

    @property
    def cv_mode(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is in CV mode
        """
        return FuGDigitalVal(int(self._fug.get_register(self._cv_mode)))

    @property
    def cc_mode(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is in CC mode
        """
        return FuGDigitalVal(int(self._fug.get_register(self._cc_mode)))

    @property
    def reg_3(self) -> FuGDigitalVal:
        """
        For special applications.

        :return: input from bit 3-REG
        """
        return FuGDigitalVal(int(self._fug.get_register(self._reg_3)))

    @property
    def x_stat(self) -> FuGPolarities:
        """

        :return: polarity of HVPS with polarity reversal
        """
        return FuGPolarities(int(self._fug.get_register(self._x_stat)))

    @property
    def on(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply ON
        """
        return FuGDigitalVal(int(self._fug.get_register(self._on)))

    @property
    def digital_control(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is digitally controlled
        """
        return FuGDigitalVal(int(self._fug.get_register(self._digital_control)))

    @property
    def analog_control(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is controlled by the analog interface
        """
        return FuGDigitalVal(int(self._fug.get_register(self._analog_control)))

    @property
    def calibration_mode(self) -> FuGDigitalVal:
        """

        :return: shows 1 if power supply is in calibration mode
        """
        return FuGDigitalVal(int(self._fug.get_register(self._calibration_mode)))


class FuGProbusVConfigRegisters:
    """
    Configuration and Status values, acc. 4.2.5
    """

    def __init__(self, fug, super_register: FuGProbusVRegisterGroups):

        self._fug = fug

        _super_register = super_register.value

        self._terminator = _super_register + "T"
        self._status = _super_register + "S"
        self._srq_status = _super_register + "QS"
        self._srq_mask = _super_register + "QM"
        self._execute_on_x = _super_register + "X"
        self._readback_data = _super_register + "N"
        self._most_recent_error = _super_register + "E"

    @property
    def terminator(self) -> FuGTerminators:
        """
        Terminator character for answer strings from ADDA

        :return: FuGTerminators
        """
        return FuGTerminators(int(self._fug.get_register(self._terminator)))

    @terminator.setter
    def terminator(self, value: Union[int, FuGTerminators]):
        """
        Sets the terminator character for answer string from ADDA

        :param value: index from FuGTerminators
        :raise FuGError: if index is not in FuGTerminators
        """
        try:
            self._fug.set_register(self._terminator, FuGTerminators(value))
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            FuGErrorcodes("E165").raise_()

    @property
    def status(self) -> str:
        """
        Statusbyte as a string of 0/1. Combined status (compatibel to Probus IV),
        MSB first:
        Bit 7: I-REG
        Bit 6: V-REG
        Bit 5: ON-Status
        Bit 4: 3-Reg
        Bit 3: X-Stat (polarity)
        Bit 2: Cal-Mode
        Bit 1: unused
        Bit 0: SEL-D

        :return: string of 0/1
        """
        return self._fug.get_register(self._status)

    @status.setter
    def status(self, _):
        """
        Stautsbyte is read-only

        :raise FuGError: read-only
        """
        FuGErrorcodes("E206").raise_()

    @property
    def srq_status(self) -> str:
        """
        SRQ-Statusbyte output as a decimal number:
        Bit 2: PS is in CC mode
        Bit 1: PS is in CV mode

        :return: representative string
        """
        return self._fug.get_register(self._srq_status)

    @srq_status.setter
    def srq_status(self, _):
        """
        SRQ-Statusbyte is read-only

        :raise FuGError: read-only
        """
        FuGErrorcodes("E206").raise_()

    @property
    def srq_mask(self) -> int:
        """
        SRQ-Mask, Service-Request
        Enable status bits for SRQ
        0: no SRQ
        Bit 2: SRQ on change of status to CC
        Bit 1: SRQ on change to CV

        :return: representative integer value
        """
        return int(float(self._fug.get_register(self._srq_mask)))

    @srq_mask.setter
    def srq_mask(self, value: int):
        """
        Sets the SRQ-Mask

        :param value: representative integer value
        """
        self._fug.set_register(self._srq_mask, value)

    @property
    def execute_on_x(self) -> FuGDigitalVal:
        """
        status of Execute-on-X

        :return: FuGDigitalVal of the status
        """
        return FuGDigitalVal(int(self._fug.get_register(self._execute_on_x)))

    @execute_on_x.setter
    def execute_on_x(self, value: Union[int, FuGDigitalVal]):
        """
        Enable/disable the Execute-on-X-mode
        0: immediate execution
        1: execution pending until X-command

        :param value: FuGDigitalVal
        :raise FuGError: if a non FuGDigitalVal is given
        """
        try:
            if FuGDigitalVal(value) is FuGDigitalVal.YES:
                self._fug.set_register(self._execute_on_x, FuGDigitalVal.YES)
            else:
                self._fug.set_register(self._execute_on_x, FuGDigitalVal.NO)
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            FuGErrorcodes("E115").raise_()

    @property
    def readback_data(self) -> FuGReadbackChannels:
        """
        Preselection of readout data for Trigger-on-Talk

        :return: index for the readback channel
        """
        return FuGReadbackChannels(int(self._fug.get_register(self._readback_data)))

    @readback_data.setter
    def readback_data(self, value: Union[int, FuGReadbackChannels]):
        """
        Sets the readback channel according to the index given within the
        FuGReadbackChannels

        :param value: index of readback channel
        :raise FuGError: if index in not in FuGReadbackChannels
        """
        try:
            self._fug.set_register(self._readback_data, FuGReadbackChannels(value))
        except ValueError as e:
            logger.error(str(e), exc_info=e)
            FuGErrorcodes("E135").raise_()

    @property
    def most_recent_error(self) -> FuGErrorcodes:
        """
        Reads the Error-Code of the most recent command

        :return FuGError:
        :raise FuGError: if code is not "E0"
        """
        return FuGErrorcodes(self._fug.get_register(self._most_recent_error))

    @most_recent_error.setter
    def most_recent_error(self, _):
        FuGErrorcodes("E666").raise_()


class FuG(FuGProbusV):
    """
    FuG power supply device class.

    The power supply is controlled over a FuG ADDA Interface with the PROBUS V protocol
    """

    def __init__(self, com, dev_config=None):
        """
        Constructor for configuring the power supply.

        :param com:
        :param dev_config:
        """

        # Call superclass constructor
        super().__init__(com, dev_config)

        self._id_string = ""
        """ID String of the device (will be retrieved after com is opened) contains
        Serial number and model"""

        # Serial number of the device (will be retrieved after com is opened)
        self._serial_number = ""
        # model class of the device (derived from serial number)
        self._model = ""
        # maximum output current of the hardware
        self._max_current_hardware = 0
        # maximum output charging power of the hardware
        self._max_power_hardware = 0
        # maximum output voltage of the hardware
        self._max_voltage_hardware = 0

        self._voltage = FuGProbusVSetRegisters(
            self, FuGProbusVRegisterGroups("SETVOLTAGE")
        )
        self._current = FuGProbusVSetRegisters(
            self, FuGProbusVRegisterGroups("SETCURRENT")
        )
        self._outX0 = FuGProbusVDORegisters(self, FuGProbusVRegisterGroups("OUTPUTX0"))
        self._outX1 = FuGProbusVDORegisters(self, FuGProbusVRegisterGroups("OUTPUTX1"))
        self._outX2 = FuGProbusVDORegisters(self, FuGProbusVRegisterGroups("OUTPUTX2"))
        self._outXCMD = FuGProbusVDORegisters(
            self, FuGProbusVRegisterGroups("OUTPUTXCMD")
        )
        self._on = FuGProbusVDORegisters(self, FuGProbusVRegisterGroups("OUTPUTONCMD"))
        self._voltage_monitor = FuGProbusVMonitorRegisters(
            self, FuGProbusVRegisterGroups("MONITOR_V")
        )
        self._current_monitor = FuGProbusVMonitorRegisters(
            self, FuGProbusVRegisterGroups("MONITOR_I")
        )
        self._di = FuGProbusVDIRegisters(self, FuGProbusVRegisterGroups("INPUT"))
        self._config_status = FuGProbusVConfigRegisters(
            self, FuGProbusVRegisterGroups("CONFIG")
        )

    def __repr__(self):
        return f"{self._id_string}"

    @property
    def max_current_hardware(self) -> Number:
        """
        Returns the maximal current which could provided with the power supply

        :return:
        """
        return self._max_current_hardware

    @property
    def max_voltage_hardware(self) -> Number:
        """
        Returns the maximal voltage which could provided with the power supply

        :return:
        """
        return self._max_voltage_hardware

    @property
    def max_current(self) -> Number:
        """
        Returns the maximal current which could provided within the test setup

        :return:
        """
        return self.current._max_setvalue

    @property
    def max_voltage(self) -> Number:
        """
        Returns the maximal voltage which could provided within the test setup

        :return:
        """
        return self.voltage._max_setvalue

    @property
    def voltage(self) -> FuGProbusVSetRegisters:
        """
        Returns the registers for the voltage output

        :return:
        """
        return self._voltage

    @voltage.setter
    def voltage(self, value: Number):
        """
        The output voltage can be set directly with this property.

        This is the short version for "self.voltage.setvalue"

        :param value: voltage in V
        """
        self.voltage.setvalue = value

    @property
    def current(self) -> FuGProbusVSetRegisters:
        """
        Returns the registers for the current output

        :return:
        """
        return self._current

    @current.setter
    def current(self, value: Number):
        """
        The output current can be set directly with this property.

        This is the short version for "self.current.setvalue"

        :param value: Current in A
        """
        self.current.setvalue = value

    @property
    def outX0(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the digital output X0

        :return: FuGProbusVDORegisters
        """
        return self._outX0

    @property
    def outX1(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the digital output X1

        :return: FuGProbusVDORegisters
        """
        return self._outX1

    @property
    def outX2(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the digital output X2

        :return: FuGProbusVDORegisters
        """
        return self._outX2

    @property
    def outXCMD(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the digital outputX-CMD

        :return: FuGProbusVDORegisters
        """
        return self._outXCMD

    @property
    def on(self) -> FuGProbusVDORegisters:
        """
        Returns the registers for the output switch to turn the output on or off

        :return: FuGProbusVDORegisters
        """
        return self._on

    @on.setter
    def on(self, value: Union[int, FuGDigitalVal]):
        """
        The output can be directly en- and disabled with this property.

        It is the short version for "self.on.out"

        :param value: instance of FuGDigitalVal
        """
        self.on.out = value

    @property
    def voltage_monitor(self) -> FuGProbusVMonitorRegisters:
        """
        Returns the registers for the voltage monitor.

        A typically usage will be "self.voltage_monitor.value" to measure the output
        voltage

        :return:
        """
        return self._voltage_monitor

    @property
    def current_monitor(self) -> FuGProbusVMonitorRegisters:
        """
        Returns the registers for the current monitor.

        A typically usage will be "self.current_monitor.value" to measure the output
        current

        :return:
        """
        return self._current_monitor

    @property
    def di(self) -> FuGProbusVDIRegisters:
        """
        Returns the registers for the digital inputs

        :return: FuGProbusVDIRegisters
        """
        return self._di

    @property
    def config_status(self) -> FuGProbusVConfigRegisters:
        """
        Returns the registers for the registers with the configuration and status values

        :return: FuGProbusVConfigRegisters
        """
        return self._config_status

    def start(self, max_voltage=0, max_current=0) -> None:
        """
        Opens the communication protocol and configures the device.

        :param max_voltage: Configure here the maximal permissible voltage which is
            allowed in the given experimental setup
        :param max_current: Configure here the maximal permissible current which is
            allowed in the given experimental setup
        """

        # starting FuG Probus Interface
        super().start()

        self.voltage._max_setvalue = max_voltage
        self.current._max_setvalue = max_current

        # find out which type of source this is:
        self.identify_device()

    def identify_device(self) -> None:
        """
        Identify the device nominal voltage and current based on its model number.

        :raises SerialCommunicationIOError: when communication port is not opened
        """
        id_string = str(self.command(FuGProbusIVCommands("ID")))
        # "'FUG HCK
        # 800
        # - 20 000
        # MOD 17022-01-01'"
        # regex to find the model of the device
        regex_model = (
            "FUG (?P<model>[A-Z]{3})"
            " (?P<power>[0-9 ]+)"
            " - (?P<voltage>[0-9 ]+)"
            " MOD (?P<sn>[0-9-]+)"
        )

        result = re.search(regex_model, id_string)
        if not result:
            raise FuGError(
                f'The device with the ID string "{id_string}" could not be recognized.'
            )

        self._id_string = id_string
        results = result.groupdict()
        self._model = results.get("model")
        self._max_power_hardware = int(
            results.get("power").replace(" ", "")  # type: ignore
        )
        self._max_voltage_hardware = int(
            results.get("voltage").replace(" ", "")  # type: ignore
        )
        self._max_current_hardware = (
            2 * self._max_power_hardware / self._max_voltage_hardware
        )
        self._serial_number = results.get("sn")

        logger.info(f"Device {id_string} successfully identified:")
        logger.info(f"Model class: {self._model}")
        logger.info(f"Maximal voltage: {self._max_voltage_hardware} V")
        logger.info(f"Maximal current: {self._max_current_hardware} A")
        logger.info(f"Maximal charging power: {self._max_power_hardware} J/s")
        logger.info(f"Serial number: {self._serial_number}")

        # if limits for test setup were not predefined, set them to hardware limits
        # or if the previous limits were to high, limit them to the hardware limits
        if 0 == self.max_voltage:
            self.voltage._max_setvalue = self.max_voltage_hardware
        elif self.max_voltage > self.max_voltage_hardware:
            logger.warning(
                f"FuG power source should supply up to "
                f"{self.max_voltage} V, but the hardware only goes up "
                f"to {self.max_voltage_hardware} V."
            )
            self.voltage._max_setvalue = self.max_voltage_hardware
        logger.info(
            f"For this setup the maximal output voltage of the power "
            f"supply is limited to {self.max_voltage} V."
        )

        if 0 == self.max_current:
            self.current._max_setvalue = self.max_current_hardware
        elif self.max_current > self.max_current_hardware:
            logger.warning(
                f"FuG power source should supply up to "
                f"{self.max_current} A, but the hardware only goes up "
                f"to {self.max_current_hardware} A."
            )
            self.current._max_setvalue = self.max_current_hardware
        logger.info(
            f"For this setup the maximal output current of the power "
            f"supply is limited to {self.max_current} A."
        )


class FuGError(DeviceException):
    """
    Error with the FuG voltage source.
    """

    def __init__(self, *args, **kwargs):
        self.errorcode: str = kwargs.pop("errorcode", "")
        """
        Errorcode from the Probus, see documentation of Probus V chapter 5.
        Errors with three-digit errorcodes are thrown by this python module.
        """
        super().__init__(*args, **kwargs)
