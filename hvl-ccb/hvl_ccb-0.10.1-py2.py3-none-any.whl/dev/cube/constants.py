#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Constants, variable names for the BaseCube OPC-connected devices.
"""
from __future__ import annotations

import logging
from abc import abstractmethod
from typing import cast, Sequence, Sized, Tuple, TYPE_CHECKING

from aenum import IntEnum, Enum

from hvl_ccb.dev.base import DeviceException
from hvl_ccb.utils.enum import ValueEnum, unique, BoolEnum
from hvl_ccb.utils.validation import validate_bool, Number

if TYPE_CHECKING:
    from hvl_ccb.dev.cube import BaseCube  # pragma: no cover

logger = logging.getLogger(__name__)


class CubeError(DeviceException):
    pass


class CubeStatusChangeError(CubeError):
    pass


class CubeStopError(CubeError):
    pass


class CubeRemoteControlError(CubeError):
    pass


class CubeEarthingStickOperationError(CubeError):
    pass


class PICubeTestParameterError(CubeError):
    pass


class _BaseGetDescriptor:
    """
    Base Descriptor for attributes that are readonly.
    """

    def __init__(self, number: int, name: str):
        self.number = number
        self.name = name

    @abstractmethod
    def __get__(self, instance, owner):
        pass  # pragma: no cover

    def __set__(self, instance, state):
        msg = (
            f"It is not possible to set the {self.name}. "
            f"This parameter is readonly!"
        )
        logger.error(msg)
        raise AttributeError(msg)


@unique
class _CubeOpcEndpoint(ValueEnum):
    """
    OPC Server Endpoint strings for the BaseCube variants.
    """

    PI_CUBE = "PICube"
    BASE_CUBE = "BaseCube"


class _SupportPort:
    """
    class to collect outputs and inputs of support ports.
    """

    _PORTS: tuple = (1, 2, 3, 4, 5, 6)
    _CONTACTS: tuple = (1, 2)
    _IOS: tuple = ("Q", "I")

    def __init__(self, handle, number: int):
        self._handle: BaseCube = handle
        self._number: int = number

    def _cmd(self, io: str, contact: int) -> str:
        return f'"{io}x_Allg_Support{self._number}_{contact}"'

    @property
    def output_1(self) -> bool:
        """
        Output 1 of support port.

        :return: `True` if high, `False` if low
        """
        value = bool(self._handle.read(self._cmd("Q", 1)))
        self._log_msg(value, "Output", 1, "")
        return value

    @output_1.setter
    def output_1(self, value: bool) -> None:
        """
        Output 1 of support port.

        :param value: `True` for high output, `False` for low
        """
        validate_bool("state", value, logger)
        self._handle.write(self._cmd("Q", 1), value)
        self._log_msg(value, "Output", 1, "set to ")

    @property
    def output_2(self) -> bool:
        """
        Output 2 of support port.

        :return: `True` if high, `False` if low
        """
        value = bool(self._handle.read(self._cmd("Q", 2)))
        self._log_msg(value, "Output", 2, "")
        return value

    @output_2.setter
    def output_2(self, value: bool) -> None:
        """
        Output 2 of support port.

        :param value: `True` for high output, `False` for low
        """
        validate_bool("state", value, logger)
        self._handle.write(self._cmd("Q", 2), value)
        self._log_msg(value, "Output", 2, "set to ")

    @property
    def input_1(self) -> bool:
        """
        Input 1 of support port.

        :return: `True` if high, `False` if low
        """
        value = bool(self._handle.read(self._cmd("I", 1)))
        self._log_msg(value, "Input", 1, "")
        return value

    @property
    def input_2(self) -> bool:
        """
        Input 2 of support port

        :return: `True` if high, `False` if low
        """
        value = bool(self._handle.read(self._cmd("I", 2)))
        self._log_msg(value, "Input", 2, "")
        return value

    def _log_msg(self, value, name, contact, action) -> None:
        value_str = "HIGH" if value else "LOW"
        logger.info(f"Support {name} Port {self._number} Contact {contact} "
                    f"is {action}{value_str}")


@unique
class _BreakdownDetection(ValueEnum):
    """
    Node ID strings for the breakdown detection.
.
    """

    # Boolean read-only variable indicating whether breakdown detection and fast
    # switchoff is enabled in the system or not.
    ACTIVATED = '"DB_Fast_Switch_Off"."sx_breakdownD_active"'

    # Boolean read-only variable telling whether the fast switch-off has triggered.
    # This can also be seen using the safety circuit state, therefore no method is
    # implemented to read this out directly.
    TRIGGERED = '"DB_Fast_Switch_Off"."sx_breakdownD_triggered"'

    # Boolean writable variable to reset the fast switch-off. Toggle to re-enable.
    RESET = '"DB_Fast_Switch_Off"."sx_breakdownD_reset"'


_CEE16 = '"Qx_Allg_Socket_CEE16"'


class _T13Socket:
    """
    Set and get the state of a SEV T13 power socket.
    """

    _SOCKETS: tuple = (1, 2, 3)

    def __init__(self, socket):
        self._socket = socket
        self._CMD = f'"Qx_Allg_Socket_T13_{socket}"'

    def __get__(self, instance, owner):
        if instance is None:
            return self  # pragma: no cover
        else:
            value = bool(instance.read(self._CMD))
            state = "ON" if value else "OFF"
            logger.info(f"T13 Power Socket {self._socket} is {state}")
            return value

    def __set__(self, instance, state):
        validate_bool("state", state, logger)
        instance.write(self._CMD, state)
        state_str = "ON" if state else "OFF"
        logger.info(f"T13 Power Socket {self._socket} is switched {state_str}")


@unique
class _Safety(ValueEnum):
    """
    NodeID strings for the basic safety circuit status
    """

    # Status is a read-only integer containing the state number of the
    # BaseCube-internal state machine. The values correspond to the numbers in
    # :class:`SafetyStatus`.
    STATUS = '"DB_Safety_Circuit"."si_safe_status"'


class SafetyStatus(IntEnum):
    """
    Safety status values that are possible states returned from
    :meth:`hvl_ccb.dev.cube.base.BaseCube.status`. These
    values correspond to the states of the BaseCube's safety circuit statemachine.
    """

    # System is initializing or booting.
    INITIALIZING = 0

    # System is safe, lamps are green and some safety elements are not in place such
    # that it cannot be switched to 'RED_READY' currently.
    GREEN_NOT_READY = 1

    # System is safe and all safety elements are in place to be able to switch to
    # *ready* 'RED_READY'.
    GREEN_READY = 2

    # System is locked in red state and *ready* to go to *operate* ('RED_OPERATE') mode.
    RED_READY = 3

    # System is locked in red state and in *operate* mode, i.e. high voltage on.
    RED_OPERATE = 4

    # Fast turn off triggered and switched off the system. Reset Breakdown Detection
    # to go back to a normal state.
    QUICK_STOP = 5

    # System is in error mode.
    ERROR = 6


class _SafetyStatusTransition(Enum, init="source target command"):  # type:ignore
    """
    NodeID strings for the transition between "ready" and "operate" and
    the corresponding source and target states.
    """
    #: Writable boolean for switching to Red Ready (locked, HV off) state.
    SWITCH_TO_READY = (SafetyStatus.GREEN_READY, SafetyStatus.RED_READY,
                       '"DB_Safety_Circuit"."sx_safe_switch_to_ready"')
    #: Writable boolean for switching to Red Operate (locket, HV on) state.
    SWITCH_TO_OPERATE = (SafetyStatus.RED_READY, SafetyStatus.RED_OPERATE,
                         '"DB_Safety_Circuit"."sx_safe_switch_to_operate"')


STOP_SAFETY_STATUSES: Tuple[SafetyStatus, ...] = (
    cast(SafetyStatus, SafetyStatus.GREEN_NOT_READY),
    cast(SafetyStatus, SafetyStatus.GREEN_READY),
)
"""BaseCube's safety statuses required to close the connection to the device.
"""


@unique
class _Power(ValueEnum):
    """
    Variable NodeID strings concerning power data.

    """

    # Primary voltage in volts, measured by the power inverter at its output.
    # (read-only)
    VOLTAGE_PRIMARY = '"DB_Datamanagement"."si_output_SC_voltage"'

    # Primary current in ampere, measured by the power inverter. (read-only)
    CURRENT_PRIMARY = '"DB_Datamanagement"."si_output_SC_current"'

    # Power setup that is configured using the BaseCube HMI. The value corresponds to
    # the ones in :class:`PowerSetup`. (read-only)
    SETUP = '"DB_Safety_Circuit"."si_power_setup"'

    # Voltage slope in V/s or kV/s (depends on Power Setup).
    VOLTAGE_SLOPE = '"DB_Powercontrol"."si_set_dUdT"'

    # Target voltage setpoint in V or kV (depends on Power Setup).
    VOLTAGE_TARGET = '"DB_Powercontrol"."si_set_voltage"'

    # Maximum voltage allowed by the current experimental setup in V or kV
    # (depends on Power Setup).. (read-only)
    VOLTAGE_MAX = '"DB_Powercontrol"."si_voltage_limit_panel"'

    # Power inverter output frequency. (read-only)
    FREQUENCY = '"DB_Datamanagement"."si_converter_frequency"'

    # Polarity of the output if a DC PowerSetup (7 or 8) is used.
    # Returns True if positive
    POLARITY = '"DB_Powercontrol"."sx_set_polarity"'

    # actual measured output voltage in V or kV (depends on Power Setup).
    VOLTAGE_ACTUAL = '"DB_Measurements"."si_actual_voltage"'


class Polarity(IntEnum):
    NEGATIVE = 0
    POSITIVE = 1


class PowerSetup(IntEnum, init="value slope_min slope_max scale unit"):  # type:ignore
    """
    Possible power setups corresponding to the value of variable :attr:`Power.setup`.
    The values for slope_min are experimentally defined, below these values the slope
    is more like a staircase

    The name of the first argument needs to be 'value', otherwise the IntEnum is
    not working correctly.
    """

    # No safety switches, uses only safety components (doors, fence, earthing...)
    # without any power source.
    NO_SOURCE = 0, 0, 0, 1, ""

    # For PICube: External power supply fed through blue 25A power plug input using
    # isolation transformer and safety switches of the PICube
    # For BaseCube: Use of an external safety switch attached to the BaseCube.
    EXTERNAL_SOURCE = 1, 0, 0, 1, ""

    # AC setup with one MWB transformer set to 50 kV maximum voltage.
    AC_50KV = 2, 100, 6000, 1e-3, "kV"

    # AC setup with one MWB transformer set to 100 kV maximum voltage.
    AC_100KV = 3, 100, 15000, 1e-3, "kV"

    # AC setup with two MWB transformers, one configured to a output voltage
    # of 100 kV and the other to 50 kV, resulting in a total maximum voltage of 150 kV.
    AC_150KV = 4, 200, 15000, 1e-3, "kV"

    # AC setup with two MWB transformers both configured to a output voltage
    # of 100 kV, resulting in a total maximum voltage of 200kV.
    AC_200KV = 5, 200, 15000, 1e-3, "kV"

    # Direct control of the internal power inverter, controlling of the primary voltage
    # output of the PICube itself. The maximum voltage at the output of the PICube
    # is 200 V. No feedback loop with a measurement transformer is used.
    POWER_INVERTER_220V = 6, 0.2, 15, 1, "V"

    # DC setup with one AC transformer configured to 100 kV and a rectifier circuit.
    # The maximum DC voltage is 140 kV.
    DC_140KV = 7, 300, 15000, 1e-3, "kV"

    # DC setup with one AC transformer configured to 100 kV and a Greinacher
    # voltage doubler circuit.
    # OR a DC setup with two AC transformers both configured to 100 kV and a rectifier
    # circuit. Both setup are resulting in DC voltage of 280 kV.
    DC_280KV = 8, 300, 15000, 1e-3, "kV"

    # Impulse setup with one AC transformer configured to 100 kV and a rectifier
    # circuit, which results in a maximum DC voltage of 140 kV. The impulse is
    # triggered with a spark gap.
    IMPULSE_140KV = 9, 300, 15000, 1e-3, "kV"


DC_POWER_SETUPS: Tuple[PowerSetup, ...] = (
    cast(PowerSetup, PowerSetup.DC_140KV),
    cast(PowerSetup, PowerSetup.DC_280KV),
)

AC_POWER_SETUPS: Tuple[PowerSetup, ...] = (
    cast(PowerSetup, PowerSetup.AC_50KV),
    cast(PowerSetup, PowerSetup.AC_100KV),
    cast(PowerSetup, PowerSetup.AC_150KV),
    cast(PowerSetup, PowerSetup.AC_200KV),
)


class _MeasurementChannel:
    """
    Measurement Channel with properties for the value and the ratio.
    """

    def __init__(self, handle, number: int, input_noise: Number):
        self._handle: BaseCube = handle
        self._number: int = number
        self._input_noise: Number = input_noise
        self._CMD_SCALE: str = f'"DB_Measurements"."sx_volts_input_{number}"'
        self._CMD_VOLTAGE: str = f'"DB_Measurements"."si_scaled_Voltage_Input_{number}"'
        self._CMD_RATIO: str = f'"DB_Measurements"."si_Divider_Ratio_{number}"'

    @property
    def voltage(self) -> float:
        """
        Measured voltage of the measurement channel.

        :return: in V
        """
        value = float(self._handle.read(self._CMD_VOLTAGE))
        scale_unit = self._handle.read(self._CMD_SCALE)
        if scale_unit:
            value_return = value * 1e3
            unit = "kV"
        else:
            value_return = value
            unit = "V"
        logger.info(
            f"Measurement Voltage of Channel {self._number} "
            f"is {value:_.2f} {unit}"
        )
        return value_return

    @property
    def ratio(self) -> float:
        """
        Set ratio for the measurement channel.

        :return: in 1
        """
        value = float(self._handle.read(self._CMD_RATIO))
        logger.info(f"Measurement Ratio of Channel {self._number} is {value}")
        return value

    @property
    def noise_level(self) -> Number:
        return self._input_noise


class EarthingStickStatus(IntEnum):
    """
    Status of an earthing stick. These are the possible values in the status integer
    e.g. in :attr:`_EarthingStick.status`.
    """

    # Earthing stick is deselected and not enabled in safety circuit. To get out of
    # this state, the earthing has to be enabled in the BaseCube HMI setup.
    INACTIVE = 0

    # Earthing is closed (safe).
    CLOSED = 1

    # Earthing is open (not safe).
    OPEN = 2

    # Earthing is in error, e.g. when the stick did not close correctly or could not
    # open.
    ERROR = 3


class EarthingStickOperatingStatus(IntEnum):
    """
    Operating Status for an earthing stick. Stick can be used in auto or manual mode.
    """

    AUTO = 0
    MANUAL = 1


class EarthingStickOperation(BoolEnum):
    """
    Operation of the earthing stick in manual operating mode. Can be closed of opened.
    """

    OPEN = False
    CLOSE = True


class _EarthingStick:
    """
    Earthing sticks with status, operating status (manual and auto) and manual operate.
    """

    _STICKS: tuple = (1, 2, 3, 4, 5, 6)

    def __init__(self, handle, number: int):
        self._handle: BaseCube = handle
        self._number: int = number
        self._CMD_STATUS: str = (
            f'"DB_Safety_Circuit"."Earthstick_{number}"."si_HMI_Status"'
        )
        self._CMD_OPERATING_STATUS: str = (
            f'"DB_Safety_Circuit"."Earthstick_{number}"."sx_manual_control_active"'
        )
        self._CMD_MANUAL: str = (
            f'"DB_Safety_Circuit"."Earthstick_{number}"."sx_earthing_manually"'
        )

    @property
    def status(self) -> EarthingStickStatus:
        """
        Status of the earthing stick.

        :return: Status of the earthing stick.
        """
        value = EarthingStickStatus(self._handle.read(self._CMD_STATUS))
        logger.info(f"Status of Earthing Stick {self._number} is {value.name}")
        return value

    @property
    def operating_status(self) -> EarthingStickOperatingStatus:
        """
        Earthing stick operating status, if 'manual' the stick can be controlled by the
        user.

        :return: Earthing stick operating status, can be either auto or manual
        """
        value = EarthingStickOperatingStatus(
            self._handle.read(self._CMD_OPERATING_STATUS)
        )
        logger.info(
            f"Operating Status of Earthing Stick {self._number} is {value.name}"
        )
        return value

    @property
    def operate(self) -> EarthingStickOperation:
        """
        Operation of an earthing stick, which is set to manual operation.

        :return: Earthing stick operation status, can be open or close
        """
        value = EarthingStickOperation(self._handle.read(self._CMD_MANUAL))
        logger.info(f"Manual Status of Earthing Stick {self._number} is {value}")
        return value

    @operate.setter
    def operate(self, operation: EarthingStickOperation) -> None:
        """
        Operation of an earthing stick, which is set to manual operation. If an earthing
        stick is set to manual, it stays closed even if the system is in states
        RED_READY or RED_OPERATE.

        :param operation: earthing stick manual status (close or open)
        :raises CubeEarthingStickOperationError: when operating status of given
            number's earthing stick is not manual
        """
        operation = EarthingStickOperation(operation)
        if self._handle.status not in (
            SafetyStatus.RED_READY, SafetyStatus.RED_OPERATE
        ):
            msg = (f'Cube needs to be in state "RED_READY" or "RED_OPERATE" '
                   f"to operate Earthing Stick manually, "
                   f'but is in "{self._handle.status.name}".')
            logger.error(msg)
            raise CubeEarthingStickOperationError(msg)
        if self.operating_status == EarthingStickOperatingStatus.MANUAL:
            self._handle.write(self._CMD_MANUAL, operation)
            logger.info(f"Earthing Stick {self._number} is set to {operation}")
        else:
            msg = (f"Operation of the Earthing Stick {self._number} is not possible, "
                   f"as the feature is not activated in the Cube Setup.")
            logger.error(msg)
            raise CubeEarthingStickOperationError(msg)


@unique
class _Errors(ValueEnum):
    """
    Variable NodeID strings for information regarding error, warning and message
    handling.
    """

    #: Boolean read-only variable telling if a message is active.
    MESSAGE = '"DB_Message_Buffer"."Info_active"'

    #: Boolean read-only variable telling if a warning is active.
    WARNING = '"DB_Message_Buffer"."Warning_active"'

    #: Boolean read-only variable telling if a stop is active.
    STOP = '"DB_Message_Buffer"."Stop_active"'

    #: Writable boolean for the error quit button.
    QUIT = '"DB_Message_Buffer"."Reset_button"'


class DoorStatus(IntEnum):
    """
    Possible status values for doors.
    """

    #: not enabled in BaseCube HMI setup, this door is not supervised.
    INACTIVE = 0

    #: Door is open.
    OPEN = 1

    #: Door is closed, but not locked.
    CLOSED = 2

    #: Door is closed and locked (safe state).
    LOCKED = 3

    #: Door has an error or was opened in locked state (either with emergency stop or
    #: from the inside).
    ERROR = 4


class _Door(_BaseGetDescriptor):
    """
    Get the status of a safety fence door. See :class:`constants.DoorStatus` for
    possible returned door statuses.
    """

    def __init__(self, number, name):
        super().__init__(number, name)
        self._CMD = f'"DB_Safety_Circuit"."Door_{number}"."si_HMI_status"'

    def __get__(self, instance, owner):
        """
        :return: the door status
        """
        if instance is None:
            return self  # pragma: no cover
        else:
            value = DoorStatus(instance.read(self._CMD))
            logger.info(f"Door {self.number} is {value.name}")
            return value


class EarthingRodStatus(IntEnum):
    """
    Possible status values for earthing rods.
    """

    #: earthing rod is somewhere in the experiment
    #: and blocks the start of the experiment
    EXPERIMENT_BLOCKED = 0

    #: earthing rod is hanging next to the door, experiment is ready to operate
    EXPERIMENT_READY = 1


class _EarthingRod(_BaseGetDescriptor):
    """
    Get the status of a earthing rod. See :class:`constants.EarthingRodStatus` for
    possible returned earthing rod statuses.
    """

    def __init__(self, number, name):
        super().__init__(number, name)
        self._CMD = f'"DB_Safety_Circuit"."Door_{number}"."Ix_earthingrod"'

    def __get__(self, instance, owner):
        """
        :return: the earthing rod status
        """
        if instance is None:
            return self  # pragma: no cover
        else:
            value = EarthingRodStatus(instance.read(self._CMD))
            if value == EarthingRodStatus.EXPERIMENT_READY:
                status = "NOT "
            else:
                status = ""
            logger.info(
                f"Earthing Rod {self.number} is {status}blocking the Experiment"
            )
            return value


class _PrefixedNumbersEnumBase(ValueEnum):
    """
    Base class for enums with "{prefix}{n}" instance names, where n=1..N.
    """

    @classmethod
    def range(cls) -> Sequence[int]:
        """
        Integer range of all channels.

        :return: sequence of channel numbers
        """
        return range(1, len(cast(Sized, cls)) + 1)

    @classmethod
    def _validate_number(cls, number: int):
        """
        Validate enum instance number.

        :param number: the enum instance number (1..N)
        :raises ValueError: when enum instance number is not in 1..N range
        """
        if number not in cls.range():
            raise ValueError(
                f"{cls._prefix()} number must be one of {list(cls.range())}"
            )

    @classmethod
    def _prefix(cls) -> str:
        """
        Enum instances name prefix: "{prefix}{n}"

        :return: enum instances prefix string
        """
        raise NotImplementedError("Implement in subclass")  # pragma: no cover

    @property
    def number(self) -> int:
        """
        Get corresponding enum instance number.

        :return: enum instance number (1..N)
        """
        # Py >=3.9: self.name.removeprefix()
        return int(self.name[len(self._prefix()):])

    # no type return as it would be a arguably too complex/obscure;
    # cf. https://github.com/python/typing/issues/58#issuecomment-326240794
    @classmethod
    def get(cls, number: int):
        """
        Get the enum instance for a given number.

        :param number: the instance number (1..N)
        :return: the enum instance for the given number.
        :raises ValueError: when instance number is not in the 1..N range
        """
        cls._validate_number(number)
        return getattr(cls, f"{cls._prefix()}{number}")


NUMBER_OF_ALARMS = 152


class _AlarmEnumBase(_PrefixedNumbersEnumBase):
    """
    Base class for enums with "Alarm{n}" instance names, where n=1..N.
    """

    @classmethod
    def _prefix(cls) -> str:
        return "ALARM_"

    @classmethod
    def alarm(cls, number: int):
        """
        Get the enum instance for a given alarm number.

        :param number: the alarm number (1..N)
        :return: the enum instance for the alarm number.
        :raises ValueError: when alarm number is not in the 1..N range
        """
        return cls.get(number)


_Alarms = unique(
    _AlarmEnumBase(
        "Alarms",
        {f"{_AlarmEnumBase._prefix()}{n}": f'"DB_Alarm_HMI"."Alarm{n}"'
         for n in range(1, NUMBER_OF_ALARMS)},
    )
)
"""
Alarms enumeration containing all variable NodeID strings for the alarm array.
"""


class _AlarmStatus(IntEnum):
    INACTIVE = 0
    ACTIVE = 1


class _AlarmsOverview:
    """
    Stores the status of all alarms / messages
    """
    def __init__(self):
        for i in _Alarms.range():
            setattr(type(self), f"alarm_{i}", _AlarmStatus.INACTIVE)


class _AlarmLevel(IntEnum):
    """
    Alarm Level for OPC alarms, the level is similar to the corresponding logging level.
    """

    NOT_DEFINED = 10
    MESSAGE = 20
    WARNING = 30
    STOP = 35


class _AlarmText(ValueEnum, init="level coming going"):  # type:ignore
    """
    This enumeration contains the message for coming and going alarms of the BaseCube
    system.
    The corresponding AlarmLevel is also stored.
    Use the :meth:`AlarmText.get_level`
    method to retrieve the alarm level of an alarm number.
    Use the :meth:`AlarmText.get_coming_message`
    method to retrieve the going message of an alarm number.
    Use the :meth:`AlarmText.get_going_message`
    method to retrieve the coming message of an alarm number.
    """

    # Safety elements
    ALARM_1 = (_AlarmLevel.STOP,
               "Emergency Stop 1 triggered", "Emergency Stop 1 released")
    ALARM_2 = (_AlarmLevel.STOP,
               "Emergency Stop 2 triggered", "Emergency Stop 2 released")
    ALARM_3 = (_AlarmLevel.STOP,
               "Emergency Stop 3 triggered", "Emergency Stop 3 released")
    ALARM_4 = _AlarmLevel.STOP, "Safety Switch 1 Error", "Safety Switch 1 Error solved"
    ALARM_5 = _AlarmLevel.STOP, "Safety Switch 2 Error", "Safety Switch 2 Error solved"
    ALARM_6 = _AlarmLevel.STOP, "Door 1 Lock Failure", "Door 1 Lock Failure solved"
    ALARM_7 = _AlarmLevel.STOP, "Door 2 Lock Failure", "Door 2 Lock Failure solved"
    ALARM_8 = _AlarmLevel.STOP, "Door 3 Lock Failure", "Door 3 Lock Failure solved"
    ALARM_9 = (_AlarmLevel.STOP, "Earthing Stick 1 Error while opening",
               "Earthing Stick 1 Error while opening solved")
    ALARM_10 = (_AlarmLevel.STOP, "Earthing Stick 2 Error while opening",
                "Earthing Stick 2 Error while opening solved")
    ALARM_11 = (_AlarmLevel.STOP, "Earthing Stick 3 Error while opening",
                "Earthing Stick 3 Error while opening solved")
    ALARM_12 = (_AlarmLevel.STOP, "Earthing Stick 4 Error while opening",
                "Earthing Stick 4 Error while opening solved")
    ALARM_13 = (_AlarmLevel.STOP, "Earthing Stick 5 Error while opening",
                "Earthing Stick 5 Error while opening solved")
    ALARM_14 = (_AlarmLevel.STOP, "Earthing Stick 6 Error while opening",
                "Earthing Stick 6 Error while opening solved")
    ALARM_15 = (_AlarmLevel.STOP, "Earthing Stick 1 Error while closing",
                "Earthing Stick 1 Error while closing solved")
    ALARM_16 = (_AlarmLevel.STOP, "Earthing Stick 2 Error while closing",
                "Earthing Stick 2 Error while closing solved")
    ALARM_17 = (_AlarmLevel.STOP, "Earthing Stick 3 Error while closing",
                "Earthing Stick 3 Error while closing solved")
    ALARM_18 = (_AlarmLevel.STOP, "Earthing Stick 4 Error while closing",
                "Earthing Stick 4 Error while closing solved")
    ALARM_19 = (_AlarmLevel.STOP, "Earthing Stick 5 Error while closing",
                "Earthing Stick 5 Error while closing solved")
    ALARM_20 = (_AlarmLevel.STOP, "Earthing Stick 6 Error while closing",
                "Earthing Stick 6 Error while closing solved")
    ALARM_21 = _AlarmLevel.STOP, "Safety Fence 1 not closed", "Safety Fence 1 closed"
    ALARM_22 = _AlarmLevel.STOP, "Safety Fence 2 not closed", "Safety Fence 2 closed"
    ALARM_23 = _AlarmLevel.STOP, "OPC Connection Error", "OPC Connection Error is gone"
    ALARM_24 = _AlarmLevel.STOP, "Grid Power Failure", "Grid Power Failure is gone"
    ALARM_25 = _AlarmLevel.STOP, "UPS Failure", "UPS Failure is gone"
    ALARM_26 = _AlarmLevel.STOP, "24V PSU Failure", "24V PSU Failure is gone"

    # Power unit
    ALARM_27 = (_AlarmLevel.STOP,
                "Power Setup and Power Switch Position are not matching",
                "Power Setup and Power Switch Position are matching again")
    ALARM_28 = (_AlarmLevel.STOP,
                "Power Inverter Failure", "Power Inverter Failure solved")
    ALARM_29 = (_AlarmLevel.STOP, "Control Loop Response Failure",
                "Control Loop Response Failure solved")
    ALARM_30 = (_AlarmLevel.STOP, "'Set Polarity' does not match with Measured Voltage",
                "'Set Polarity' matches with Measured Voltage")

    # Doors
    ALARM_41 = (_AlarmLevel.WARNING, "Door 1: Use Earthing Rod!",
                "Door 1: Earthing Rod used.")
    ALARM_42 = (_AlarmLevel.MESSAGE, "Door 1: Earthing Rod is still in Experiment.",
                "Door 1: Earthing Rod is removed from Experiment.")
    ALARM_43 = (_AlarmLevel.WARNING, "Door 2: Use Earthing Rod!",
                "Door 2: Earthing Rod used.")
    ALARM_44 = (_AlarmLevel.MESSAGE, "Door 2: Earthing Rod is still in Experiment.",
                "Door 2: Earthing Rod is removed from Experiment.")
    ALARM_45 = (_AlarmLevel.WARNING, "Door 3: Use Earthing Rod!",
                "Door 3: Earthing Rod used.")
    ALARM_46 = (_AlarmLevel.MESSAGE, "Door 3: Earthing Rod is still in Experiment.",
                "Door 3: Earthing Rod is removed from Experiment.")

    # General
    ALARM_47 = _AlarmLevel.MESSAGE, "UPS Charge < 85%", "UPS Charge >= 85%"
    ALARM_48 = _AlarmLevel.MESSAGE, "UPS running on Battery", "UPS running on Grid"
    ALARM_49 = (_AlarmLevel.WARNING, "Remove PD-Calibrator from the Circuit",
                "PD-Calibrator removed from the Circuit")
    ALARM_50 = _AlarmLevel.MESSAGE, "OPC Connection active", "OPC Connection not active"
    ALARM_57 = (_AlarmLevel.MESSAGE, "Breakdown Detection Unit triggered",
                "Breakdown Detection Unit is reset")

    # Earthing Stick
    ALARM_51 = (_AlarmLevel.MESSAGE, "Earthing Stick 1: Manual earthing enabled",
                "Earthing Stick 1: Manual earthing disabled")
    ALARM_52 = (_AlarmLevel.MESSAGE, "Earthing Stick 2: Manual earthing enabled",
                "Earthing Stick 2: Manual earthing disabled")
    ALARM_53 = (_AlarmLevel.MESSAGE, "Earthing Stick 3: Manual earthing enabled",
                "Earthing Stick 3: Manual earthing disabled")
    ALARM_54 = (_AlarmLevel.MESSAGE, "Earthing Stick 4: Manual earthing enabled",
                "Earthing Stick 4: Manual earthing disabled")
    ALARM_55 = (_AlarmLevel.MESSAGE, "Earthing Stick 5: Manual earthing enabled",
                "Earthing Stick 5: Manual earthing disabled")
    ALARM_56 = (_AlarmLevel.MESSAGE, "Earthing Stick 6: Manual earthing enabled",
                "Earthing Stick 6: Manual earthing disabled")

    # generic not defined alarm text
    NOT_DEFINED = (_AlarmLevel.NOT_DEFINED, "NO ALARM TEXT DEFINED",
                   "NO ALARM TEXT DEFINED")

    @classmethod
    def get_level(cls, alarm: int):
        """
        Get the alarm level of this enum for an alarm number.

        :param alarm: the alarm number
        :return: the alarm level for the desired alarm number
        """

        try:
            return getattr(cls, f"ALARM_{alarm}").level
        except AttributeError:
            return getattr(cls, "NOT_DEFINED").level

    @classmethod
    def get_coming_message(cls, alarm: int):
        """
        Get the coming message of this enum for an alarm number.

        :param alarm: the alarm number
        :return: the coming alarm message for the desired alarm number
        """

        try:
            return getattr(cls, f"ALARM_{alarm}").coming
        except AttributeError:
            return getattr(cls, "NOT_DEFINED").coming

    @classmethod
    def get_going_message(cls, alarm: int):
        """
        Get the going message of this enum for an alarm number.

        :param alarm: the alarm number
        :return: the going alarm message for the desired alarm number
        """

        try:
            return getattr(cls, f"ALARM_{alarm}").going
        except AttributeError:
            return getattr(cls, "NOT_DEFINED").going


class _OpcControl(ValueEnum):
    """
    Variable NodeID strings for supervision of the OPC connection from the
    controlling workstation to the BaseCube.
    """

    # writable boolean to enable OPC remote control and display a message window on
    # the BaseCube HMI.
    ACTIVE = '"DB_OPC_Connection"."sx_OPC_active"'
    LIVE = '"DB_OPC_Connection"."sx_OPC_lifebit"'
    TIME = '"DB_OPC_Connection"."st_system_time"'


NUMBER_OF_LINES = 16


class _LineEnumBase(_PrefixedNumbersEnumBase):
    """
    Base class for enums with "input_{n}" instance names, where n=1..N.
    """

    @classmethod
    def _prefix(cls) -> str:
        return "LINE_"

    @classmethod
    def line(cls, number: int):
        """
        Get the enum instance for a given line number.

        :param number: the line number (1..M)
        :return: the enum instance for the given line number.
        :raises ValueError: when line number is not in the 1..N range
        """
        return cls.get(number)


MessageBoard = unique(
    _LineEnumBase(
        "MessageBoard",
        {
            f"{_LineEnumBase._prefix()}{n}": f'"DB_OPC_Connection"."Is_status_Line_{n}"'
            for n in range(1, NUMBER_OF_LINES)
        },
    )
)
"""
Variable NodeID strings for message board lines.
"""
