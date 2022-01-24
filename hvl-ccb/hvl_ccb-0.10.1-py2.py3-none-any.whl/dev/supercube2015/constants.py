#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Constants, variable names for the Supercube OPC-connected devices.
"""

import logging
from aenum import IntEnum

from hvl_ccb.utils.enum import ValueEnum, unique

logger = logging.getLogger(__name__)


class SupercubeOpcEndpoint(ValueEnum):
    """
    OPC Server Endpoint strings for the supercube variants.
    """

    A = "OPC.SimaticNET.S7"
    B = "OPC.SimaticNET.S7"


@unique
class GeneralSupport(ValueEnum):
    """
    NodeID strings for the support inputs and outputs.
    """

    in_1_1 = "hvl-ipc.WINAC.Support1InA"
    in_1_2 = "hvl-ipc.WINAC.Support1InB"
    in_2_1 = "hvl-ipc.WINAC.Support2InA"
    in_2_2 = "hvl-ipc.WINAC.Support2InB"
    in_3_1 = "hvl-ipc.WINAC.Support3InA"
    in_3_2 = "hvl-ipc.WINAC.Support3InB"
    in_4_1 = "hvl-ipc.WINAC.Support4InA"
    in_4_2 = "hvl-ipc.WINAC.Support4InB"
    in_5_1 = "hvl-ipc.WINAC.Support5InA"
    in_5_2 = "hvl-ipc.WINAC.Support5InB"
    in_6_1 = "hvl-ipc.WINAC.Support6InA"
    in_6_2 = "hvl-ipc.WINAC.Support6InB"
    out_1_1 = "hvl-ipc.WINAC.Support1OutA"
    out_1_2 = "hvl-ipc.WINAC.Support1OutB"
    out_2_1 = "hvl-ipc.WINAC.Support2OutA"
    out_2_2 = "hvl-ipc.WINAC.Support2OutB"
    out_3_1 = "hvl-ipc.WINAC.Support3OutA"
    out_3_2 = "hvl-ipc.WINAC.Support3OutB"
    out_4_1 = "hvl-ipc.WINAC.Support4OutA"
    out_4_2 = "hvl-ipc.WINAC.Support4OutB"
    out_5_1 = "hvl-ipc.WINAC.Support5OutA"
    out_5_2 = "hvl-ipc.WINAC.Support5OutB"
    out_6_1 = "hvl-ipc.WINAC.Support6OutA"
    out_6_2 = "hvl-ipc.WINAC.Support6OutB"

    @classmethod
    def output(cls, port, contact):
        """
        Get the NodeID string for a support output.

        :param port: the desired port (1..6)
        :param contact: the desired contact at the port (1..2)
        :return: the node id string
        """

        return getattr(cls, f"out_{port}_{contact}")

    @classmethod
    def input(cls, port, contact):
        """
        Get the NodeID string for a support input.

        :param port: the desired port (1..6)
        :param contact: the desired contact at the port (1..2)
        :return: the node id string
        """

        return getattr(cls, f"in_{port}_{contact}")


@unique
class BreakdownDetection(ValueEnum):
    """
    Node ID strings for the breakdown detection.
    """

    #: Boolean read-only variable indicating whether breakdown detection and fast
    #: switchoff is enabled in the system or not.
    activated = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.Breakdowndetection.connect"

    #: Boolean read-only variable telling whether the fast switch-off has triggered.
    #: This can also be seen using the safety circuit state, therefore no method is
    #: implemented to read this out directly.
    triggered = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.Breakdowndetection.triggered"

    #: Boolean writable variable to reset the fast switch-off. Toggle to re-enable.
    reset = "hvl-ipc.WINAC.Support6OutA"


@unique
class GeneralSockets(ValueEnum):
    """
    NodeID strings for the power sockets (3x T13 and 1xCEE16).
    """

    #: SEV T13 socket No. 1 (writable boolean).
    t13_1 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.T13_1"

    #: SEV T13 socket No. 2 (writable boolean).
    t13_2 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.T13_2"

    #: SEV T13 socket No. 3 (writable boolean).
    t13_3 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.T13_3"

    #: CEE16 socket (writeable boolean).
    cee16 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.CEE16"


T13_SOCKET_PORTS = (1, 2, 3)
"""
Port numbers of SEV T13 power socket
"""


@unique
class Safety(ValueEnum):
    """
    NodeID strings for the basic safety circuit status and green/red switches "ready"
    and "operate".
    """

    #: Status is a read-only integer containing the state number of the
    #: supercube-internal state machine. The values correspond to numbers in
    #: :class:`SafetyStatus`.
    status_ready_for_red = "hvl-ipc.WINAC.SYSTEMSTATE.ReadyForRed"
    status_red = "hvl-ipc.WINAC.SYSTEMSTATE.RED"
    status_green = "hvl-ipc.WINAC.SYSTEMSTATE.GREEN"
    status_error = "hvl-ipc.WINAC.SYSTEMSTATE.ERROR"

    #: Writable boolean for switching to Red Ready (locked, HV off) state.
    switchto_ready = "hvl-ipc.WINAC.SYSTEMSTATE.RED_REQUEST"
    switchto_green = "hvl-ipc.WINAC.SYSTEMSTATE.GREEN_REQUEST"

    #: Writable boolean for switching to Red Operate (locket, HV on) state.
    switchto_operate = "hvl-ipc.WINAC.SYSTEMSTATE.switchon"

    #: Writeable boolean to manually turn on or off the horn
    horn = "hvl-ipc.WINAC.SYSTEM_INTERN.hornen"


class SafetyStatus(IntEnum):
    """
    Safety status values that are possible states returned from
    :meth:`hvl_ccb.dev.supercube.base.Supercube.get_status`. These
    values correspond to the states of the Supercube's safety circuit statemachine.
    """

    #: System is initializing or booting.
    Initializing = 0

    #: System is safe, lamps are green and some safety elements are not in place such
    #: that it cannot be switched to red currently.
    GreenNotReady = 1

    #: System is safe and all safety elements are in place to be able to switch to
    #: *ready*.
    GreenReady = 2

    #: System is locked in red state and *ready* to go to *operate* mode.
    RedReady = 3

    #: System is locked in red state and in *operate* mode, i.e. high voltage on.
    RedOperate = 4

    #: Fast turn off triggered and switched off the system. Reset FSO to go back to a
    #: normal state.
    QuickStop = 5

    #: System is in error mode.
    Error = 6


@unique
class Power(ValueEnum):
    """
    Variable NodeID strings concerning power data.
    """

    #: Primary voltage in volts, measured by the frequency converter at its output.
    #: (read-only)
    voltage_primary = "hvl-ipc.WINAC.SYSTEM_INTERN.FUVoltageprim"

    #: Primary current in ampere, measured by the frequency converter. (read-only)
    current_primary = "hvl-ipc.WINAC.SYSTEM_INTERN.FUCurrentprim"

    #: Power setup that is configured using the Supercube HMI. The value corresponds to
    #: the ones in :class:`PowerSetup`. (read-only)
    setup = "hvl-ipc.WINAC.FU.TrafoSetup"

    #: Voltage slope in V/s.
    voltage_slope = "hvl-ipc.WINAC.FU.dUdt_-1"

    #: Target voltage setpoint in V.
    voltage_target = "hvl-ipc.WINAC.FU.SOLL"

    #: Maximum voltage allowed by the current experimental setup. (read-only)
    voltage_max = "hvl-ipc.WINAC.FU.maxVoltagekV"

    #: Frequency converter output frequency. (read-only)
    frequency = "hvl-ipc.WINAC.FU.Frequency"


class PowerSetup(IntEnum):
    """
    Possible power setups corresponding to the value of variable :attr:`Power.setup`.
    """

    #: No safety switches, use only safety components (doors, fence, earthing...)
    #: without any power.
    # NoPower = 0

    #: External power supply fed through blue CEE32 input using isolation transformer
    #: and safety switches of the Supercube, or using an external safety switch
    #: attached to the Supercube Type B.
    External = 0

    #: AC voltage with MWB transformer set to 50kV maximum voltage.
    AC_SingleStage_50kV = 1

    #: AC voltage with MWB transformer set to 100kV maximum voltage.
    AC_SingleStage_100kV = 2

    #: AC voltage with two MWB transformers, one at 100kV and the other at 50kV,
    #: resulting in a total maximum voltage of 150kV.
    AC_DoubleStage_150kV = 3

    #: AC voltage with two MWB transformers both at 100kV, resulting in a total
    #: maximum voltage of 200kV
    AC_DoubleStage_200kV = 4

    #: Internal usage of the frequency converter, controlling to the primary voltage
    #: output of the supercube itself (no measurement transformer used)
    Internal = 5

    #: DC voltage with one AC transformer set to 100kV AC, resulting in 140kV DC
    DC_SingleStage_140kV = 6

    #: DC voltage with two AC transformers set to 100kV AC each, resulting in 280kV
    #: DC in total (or a single stage transformer with Greinacher voltage doubling
    #: rectifier)
    DC_DoubleStage_280kV = 7


@unique
class MeasurementsScaledInput(ValueEnum):
    """
    Variable NodeID strings for the four analog BNC inputs for measuring voltage.
    The voltage returned in these variables is already scaled with the set ratio,
    which can be read using the variables in :class:`MeasurementsDividerRatio`.
    """

    input_1 = "hvl-ipc.WINAC.SYSTEM_INTERN.AI1Volt"
    input_2 = "hvl-ipc.WINAC.SYSTEM_INTERN.AI2Volt"
    input_3 = "hvl-ipc.WINAC.SYSTEM_INTERN.AI3Volt"
    input_4 = "hvl-ipc.WINAC.SYSTEM_INTERN.AI4Volt"

    @classmethod
    def get(cls, channel: int):
        """
        Get the attribute for an input number.

        :param channel: the channel number (1..4)
        :return: the enum for the desired channel.
        """

        return getattr(cls, f"input_{channel}")


@unique
class MeasurementsDividerRatio(ValueEnum):
    """
    Variable NodeID strings for the measurement input scaling ratios. These ratios
    are defined in the Supercube HMI setup and are provided in the python module here
    to be able to read them out, allowing further calculations.
    """

    input_1 = "hvl-ipc.WINAC.SYSTEM_INTERN.DivididerRatio"

    @classmethod
    def get(cls, channel: int):
        """
        Get the attribute for an input number.

        :param channel: the channel number (1..4)
        :return: the enum for the desired channel.
        """

        return getattr(cls, f"input_{channel}")


class EarthingStickStatus(IntEnum):
    """
    Status of an earthing stick. These are the possible values in the status integer
    e.g. in :attr:`EarthingStick.status_1`.
    """

    #: Earthing stick is deselected and not enabled in safety circuit. To get out of
    #: this state, the earthing has to be enabled in the Supercube HMI setup.
    inactive = 0

    #: Earthing is closed (safe).
    closed = 1

    #: Earthing is open (not safe).
    open = 2

    #: Earthing is in error, e.g. when the stick did not close correctly or could not
    #: open.
    error = 3


@unique
class EarthingStick(ValueEnum):
    """
    Variable NodeID strings for all earthing stick statuses (read-only integer) and
    writable booleans for setting the earthing in manual mode.
    """

    status_1_closed = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_1.CLOSE"
    status_1_open = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_1.OPEN"
    status_1_connected = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_1.CONNECT"
    status_2_closed = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_2.CLOSE"
    status_2_open = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_2.OPEN"
    status_2_connected = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_2.CONNECT"
    status_3_closed = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_3.CLOSE"
    status_3_open = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_3.OPEN"
    status_3_connected = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_3.CONNECT"
    status_4_closed = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_4.CLOSE"
    status_4_open = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_4.OPEN"
    status_4_connected = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_4.CONNECT"
    status_5_closed = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_5.CLOSE"
    status_5_open = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_5.OPEN"
    status_5_connected = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_5.CONNECT"
    status_6_closed = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_6.CLOSE"
    status_6_open = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_6.OPEN"
    status_6_connected = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_6.CONNECT"

    manual_1 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_1.MANUAL"
    manual_2 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_2.MANUAL"
    manual_3 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_3.MANUAL"
    manual_4 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_4.MANUAL"
    manual_5 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_5.MANUAL"
    manual_6 = "hvl-ipc.WINAC.SYSTEM_COMPONENTS.STICK_6.MANUAL"

    @classmethod
    def status_open(cls, number: int):
        """
        Get the status enum attribute for an earthing stick number.

        :param number: the earthing stick (1..6)
        :return: the status enum
        """

        return getattr(cls, f"status_{number}_open")

    @classmethod
    def status_closed(cls, number: int):
        """
        Get the status enum attribute for an earthing stick number.

        :param number: the earthing stick (1..6)
        :return: the status enum
        """

        return getattr(cls, f"status_{number}_closed")

    @classmethod
    def status_connected(cls, number: int):
        """
        Get the status enum attribute for an earthing stick number.

        :param number: the earthing stick (1..6)
        :return: the status enum
        """

        return getattr(cls, f"status_{number}_connected")

    @classmethod
    def manual(cls, number: int):
        """
        Get the manual enum attribute for an earthing stick number.

        :param number: the earthing stick (1..6)
        :return: the manual enum
        """

        return getattr(cls, f"manual_{number}")


@unique
class Errors(ValueEnum):
    """
    Variable NodeID strings for information regarding error, warning and message
    handling.
    """

    #: Boolean read-only variable telling if a stop is active.
    stop = "hvl-ipc.WINAC.SYSTEMSTATE.ERROR"
    stop_number = "hvl-ipc.WINAC.SYSTEMSTATE.Errornumber"

    #: Writable boolean for the error quit button.
    quit = "hvl-ipc.WINAC.SYSTEMSTATE.Faultconfirmation"


class DoorStatus(IntEnum):
    """
    Possible status values for doors.
    """

    #: not enabled in Supercube HMI setup, this door is not supervised.
    inactive = 0

    #: Door is open.
    open = 1

    #: Door is closed, but not locked.
    closed = 2

    #: Door is closed and locked (safe state).
    locked = 3

    #: Door has an error or was opened in locked state (either with emergency stop or
    #: from the inside).
    error = 4


class AlarmText(ValueEnum):
    """
    This enumeration contains textual representations for all error classes (stop,
    warning and message) of the Supercube system. Use the :meth:`AlarmText.get`
    method to retrieve the enum of an alarm number.
    """

    # No alarm
    Alarm0 = "No Alarm."

    # Safety elements
    Alarm1 = "STOP Safety switch 1 error"
    Alarm2 = "STOP Safety switch 2 error"
    Alarm3 = "STOP Emergency Stop 1"
    Alarm4 = "STOP Emergency Stop 2"
    Alarm5 = "STOP Emergency Stop 3"
    Alarm6 = "STOP Door 1 lock supervision"
    Alarm7 = "STOP Door 2 lock supervision"
    Alarm8 = "STOP Door 3 lock supervision"
    Alarm9 = "STOP Earthing stick 1 error"
    Alarm10 = "STOP Earthing stick 2 error"
    Alarm11 = "STOP Earthing stick 3 error"
    Alarm12 = "STOP Earthing stick 4 error"
    Alarm13 = "STOP Earthing stick 5 error"
    Alarm14 = "STOP Earthing stick 6 error"
    Alarm17 = "STOP Source switch error"
    Alarm19 = "STOP Fence 1 error"
    Alarm20 = "STOP Fence 2 error"
    Alarm21 = "STOP Control error"
    Alarm22 = "STOP Power outage"

    # generic not defined alarm text
    not_defined = "NO ALARM TEXT DEFINED"

    @classmethod
    def get(cls, alarm: int):
        """
        Get the attribute of this enum for an alarm number.

        :param alarm: the alarm number
        :return: the enum for the desired alarm number
        """

        try:
            return getattr(cls, f"Alarm{alarm}")
        except AttributeError as e:
            logger.error(str(e), exc_info=e)
            return cls.not_defined
