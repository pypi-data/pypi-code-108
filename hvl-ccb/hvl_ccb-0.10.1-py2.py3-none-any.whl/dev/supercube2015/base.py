#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Base classes for the Supercube device.
"""

import logging
from time import sleep

from asyncua.sync import SyncNode

from hvl_ccb.configuration import configdataclass
from hvl_ccb.comm import OpcUaSubHandler, OpcUaCommunicationConfig, OpcUaCommunication
from . import constants
from ..base import SingleCommDevice
from ...utils.validation import validate_bool

logger = logging.getLogger(__name__)


class InvalidSupercubeStatusError(Exception):
    """
    Exception raised when supercube has invalid status.
    """

    pass


class SupercubeSubscriptionHandler(OpcUaSubHandler):
    """
    OPC Subscription handler for datachange events and normal events specifically
    implemented for the Supercube devices.
    """

    def datachange_notification(self, node: SyncNode, val, data):
        """
        In addition to the standard operation (debug logging entry of the datachange),
        alarms are logged at INFO level using the alarm text.

        :param node: the node object that triggered the datachange event
        :param val: the new value
        :param data:
        """

        super().datachange_notification(node, val, data)

        # assume an alarm datachange
        if node.nodeid.Identifier == constants.Errors.stop_number:
            alarm_text = constants.AlarmText.get(val)
            logger.info(alarm_text)


@configdataclass
class SupercubeConfiguration:
    """
    Configuration dataclass for the Supercube devices.
    """

    #: Namespace of the OPC variables, typically this is 3 (coming from Siemens)
    namespace_index: int = 7


@configdataclass
class SupercubeOpcUaCommunicationConfig(OpcUaCommunicationConfig):
    """
    Communication protocol configuration for OPC UA, specifications for the Supercube
    devices.
    """

    #: Subscription handler for data change events
    sub_handler: OpcUaSubHandler = SupercubeSubscriptionHandler()

    port: int = 4845


class SupercubeOpcUaCommunication(OpcUaCommunication):
    """
    Communication protocol specification for Supercube devices.
    """

    @staticmethod
    def config_cls():
        return SupercubeOpcUaCommunicationConfig


class Supercube2015Base(SingleCommDevice):
    """
    Base class for Supercube variants.
    """

    def __init__(self, com, dev_config=None):
        """
        Constructor for Supercube base class.

        :param com: the communication protocol or its configuration
        :param dev_config: the device configuration
        """

        super().__init__(com, dev_config)

    @staticmethod
    def default_com_cls():
        return SupercubeOpcUaCommunication

    def start(self) -> None:
        """
        Starts the device. Sets the root node for all OPC read and write commands to
        the Siemens PLC object node which holds all our relevant objects and variables.
        """

        logger.info("Starting Supercube Base device")
        super().start()

        logger.debug("Add monitoring nodes")
        self.com.init_monitored_nodes(
            map(  # type: ignore
                str, constants.GeneralSockets
            ),
            self.config.namespace_index,
        )
        self.com.init_monitored_nodes(
            map(  # type: ignore
                str, constants.GeneralSupport
            ),
            self.config.namespace_index,
        )
        self.com.init_monitored_nodes(
            map(  # type: ignore
                str, constants.Safety
            ),
            self.config.namespace_index,
        )

        self.com.init_monitored_nodes(
            str(constants.Errors.stop_number), self.config.namespace_index
        )

        self.com.init_monitored_nodes(
            map(  # type: ignore
                str, constants.EarthingStick
            ),
            self.config.namespace_index,
        )

        logger.debug("Finished starting")

    def stop(self) -> None:
        """
        Stop the Supercube device. Deactivates the remote control and closes the
        communication protocol.
        """

        super().stop()

    @staticmethod
    def config_cls():
        return SupercubeConfiguration

    def read(self, node_id: str):
        """
        Local wrapper for the OPC UA communication protocol read method.

        :param node_id: the id of the node to read.
        :return: the value of the variable
        """

        result = self.com.read(str(node_id), self.config.namespace_index)
        logger.debug(f"Read from node ID {node_id}: {result}")
        return result

    def write(self, node_id, value) -> None:
        """
        Local wrapper for the OPC UA communication protocol write method.

        :param node_id: the id of the node to read
        :param value: the value to write to the variable
        """

        logger.debug(f"Write to node ID {node_id}: {value}")
        self.com.write(str(node_id), self.config.namespace_index, value)

    def set_remote_control(self, state: bool) -> None:
        """
        Enable or disable remote control for the Supercube. This will effectively
        display a message on the touchscreen HMI.

        :param state: desired remote control state
        """

        raise NotImplementedError("Function does not exist in Supercube 2015.")

    def get_support_input(self, port: int, contact: int) -> bool:
        """
        Get the state of a support socket input.

        :param port: is the socket number (1..6)
        :param contact: is the contact on the socket (1..2)
        :return: digital input read state
        """

        return bool(self.read(constants.GeneralSupport.input(port, contact)))

    def get_support_output(self, port: int, contact: int) -> bool:
        """
        Get the state of a support socket output.

        :param port: is the socket number (1..6)
        :param contact: is the contact on the socket (1..2)
        :return: digital output read state
        """

        return bool(self.read(constants.GeneralSupport.output(port, contact)))

    def set_support_output(self, port: int, contact: int, state: bool) -> None:
        """
        Set the state of a support output socket.

        :param port: is the socket number (1..6)
        :param contact: is the contact on the socket (1..2)
        :param state: is the desired state of the support output
        :raises TypeError: when state is not of type bool
        """
        validate_bool("state", state, logger)
        self.write(constants.GeneralSupport.output(port, contact), state)

    def set_support_output_impulse(
        self, port: int, contact: int, duration: float = 0.2, pos_pulse: bool = True
    ) -> None:
        """
        Issue an impulse of a certain duration on a support output contact. The polarity
        of the pulse (On-wait-Off or Off-wait-On) is specified by the pos_pulse
        argument.

        This function is blocking.

        :param port: is the socket number (1..6)
        :param contact: is the contact on the socket (1..2)
        :param duration: is the length of the impulse in seconds
        :param pos_pulse: is True, if the pulse shall be HIGH, False if it shall be LOW
        :raises TypeError: when state is not of type bool
        """

        validate_bool("pos_pulse", pos_pulse, logger)
        self.set_support_output(port, contact, pos_pulse)
        sleep(duration)
        self.set_support_output(port, contact, not pos_pulse)

    def get_t13_socket(self, port: int) -> bool:
        """
        Read the state of a SEV T13 power socket.

        :param port: is the socket number, one of `constants.T13_SOCKET_PORTS`
        :return: on-state of the power socket
        """

        if port not in constants.T13_SOCKET_PORTS:
            raise ValueError(f"port not in {constants.T13_SOCKET_PORTS}: {port}")

        return bool(self.read(getattr(constants.GeneralSockets, f"t13_{port}")))

    def set_t13_socket(self, port: int, state: bool) -> None:
        """
        Set the state of a SEV T13 power socket.

        :param port: is the socket number, one of `constants.T13_SOCKET_PORTS`
        :param state: is the desired on-state of the socket
        :raises ValueError: when port is not valid
        :raises TypeError: when state is not of type bool
        """

        validate_bool("state", state, logger)

        if port not in constants.T13_SOCKET_PORTS:
            raise ValueError(f"port not in {constants.T13_SOCKET_PORTS}: {port}")

        self.write(getattr(constants.GeneralSockets, f"t13_{port}"), state)

    def get_cee16_socket(self) -> bool:
        """
        Read the on-state of the IEC CEE16 three-phase power socket.

        :return: the on-state of the CEE16 power socket
        """

        return bool(self.read(constants.GeneralSockets.cee16))

    def set_cee16_socket(self, state: bool) -> None:
        """
        Switch the IEC CEE16 three-phase power socket on or off.

        :param state: desired on-state of the power socket
        :raises TypeError: if state is not of type bool
        """

        validate_bool("state", state, logger)

        self.write(constants.GeneralSockets.cee16, state)

    def get_status(self) -> int:
        """
        Get the safety circuit status of the Supercube.

        :return: the safety status of the supercube's state machine;
            see `constants.SafetyStatus`.
        """

        ready_for_red = self.read(constants.Safety.status_ready_for_red)
        red = self.read(constants.Safety.status_red)
        green = self.read(constants.Safety.status_green)
        operate = self.read(constants.Safety.switchto_operate)
        error = self.read(constants.Safety.status_error)
        triggered = self.read(constants.BreakdownDetection.triggered)
        fso_active = self.read(constants.BreakdownDetection.activated)

        if error:
            return constants.SafetyStatus.Error

        if triggered and fso_active:
            return constants.SafetyStatus.QuickStop

        if not ready_for_red and not red and green:
            return constants.SafetyStatus.GreenNotReady

        if ready_for_red and not red and not operate:
            return constants.SafetyStatus.GreenReady

        if red and not green and not operate:
            return constants.SafetyStatus.RedReady

        if red and not green and operate:
            return constants.SafetyStatus.RedOperate

        raise InvalidSupercubeStatusError(
            f"ready_for_red: {ready_for_red}, red: {red}, green: {green}, "
            f"operate: {operate}, triggered: {triggered}, fso_active: {fso_active}"
        )

    def ready(self, state: bool) -> None:
        """
        Set ready state. Ready means locket safety circuit, red lamps, but high voltage
        still off.

        :param state: set ready state
        """

        if state:
            if self.get_status() is constants.SafetyStatus.GreenReady:
                self.write(constants.Safety.switchto_ready, True)
                sleep(0.02)
                self.write(constants.Safety.switchto_ready, False)
        else:
            self.write(constants.Safety.switchto_green, True)
            sleep(0.02)
            self.write(constants.Safety.switchto_green, False)

    def operate(self, state: bool) -> None:
        """
        Set operate state. If the state is RedReady, this will turn on the high
        voltage and close the safety switches.

        :param state: set operate state
        """

        if state:
            if self.get_status() is constants.SafetyStatus.RedReady:
                self.write(constants.Safety.switchto_operate, True)
        else:
            self.write(constants.Safety.switchto_operate, False)

    def get_measurement_ratio(self, channel: int) -> float:
        """
        Get the set measurement ratio of an AC/DC analog input channel. Every input
        channel has a divider ratio assigned during setup of the Supercube system.
        This ratio can be read out.

        **Attention:** Supercube 2015 does not have a separate ratio for every analog
        input. Therefore there is only one ratio for ``channel = 1``.

        :param channel: number of the input channel (1..4)
        :return: the ratio
        """

        return float(self.read(constants.MeasurementsDividerRatio.get(channel)))

    def get_measurement_voltage(self, channel: int) -> float:
        """
        Get the measured voltage of an analog input channel. The voltage read out
        here is already scaled by the configured divider ratio.

        **Attention:** In contrast to the *new* Supercube, the old one returns here
        the input voltage read at the ADC. It is not scaled by a factor.

        :param channel: number of the input channel (1..4)
        :return: measured voltage
        """

        return float(self.read(constants.MeasurementsScaledInput.get(channel)))

    def get_earthing_status(self, number: int) -> int:
        """
        Get the status of an earthing stick, whether it is closed, open or undefined
        (moving).

        :param number: number of the earthing stick (1..6)
        :return: earthing stick status; see constants.EarthingStickStatus
        """

        connected = self.read(constants.EarthingStick.status_connected(number))
        open_ = self.read(constants.EarthingStick.status_open(number))
        closed = self.read(constants.EarthingStick.status_closed(number))

        if not connected:
            return constants.EarthingStickStatus.inactive

        if open_ and not closed:
            return constants.EarthingStickStatus.open

        if not open_ and closed:
            return constants.EarthingStickStatus.closed

        return constants.EarthingStickStatus.error

    def get_earthing_manual(self, number: int) -> bool:
        """
        Get the manual status of an earthing stick. If an earthing stick is set to
        manual, it is closed even if the system is in states RedReady or RedOperate.

        :param number: number of the earthing stick (1..6)
        :return: earthing stick manual status
        """

        return bool(self.read(constants.EarthingStick.manual(number)))

    def set_earthing_manual(self, number: int, manual: bool) -> None:
        """
        Set the manual status of an earthing stick. If an earthing stick is set to
        manual, it is closed even if the system is in states RedReady or RedOperate.

        :param number: number of the earthing stick (1..6)
        :param manual: earthing stick manual status (True or False)
        """

        if self.get_status() is constants.SafetyStatus.RedOperate:
            raise RuntimeError("Status is Red Operate, should not move earthing.")
        self.write(constants.EarthingStick.manual(number), manual)

    def quit_error(self) -> None:
        """
        Quits errors that are active on the Supercube.
        """

        self.write(constants.Errors.quit, True)
        sleep(0.1)
        self.write(constants.Errors.quit, False)

    def horn(self, state: bool) -> None:
        """
        Turns acoustic horn on or off.

        :param state: Turns horn on (True) or off (False)
        """
        self.write(constants.Safety.horn, state)

    def get_door_status(self, door: int) -> constants.DoorStatus:
        """
        Get the status of a safety fence door. See :class:`constants.DoorStatus` for
        possible returned door statuses.

        :param door: the door number (1..3)
        :return: the door status
        """

        raise NotImplementedError(
            "Door status not supported in old Supercube 2015 version."
        )
