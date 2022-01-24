#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Classes for the BaseCube device.
"""

import logging
from collections import deque
from datetime import datetime, timedelta
from itertools import cycle, product
from time import sleep, time
from typing import List, Sequence, cast, Optional, Union

from asyncua.sync import SyncNode

from hvl_ccb.comm import (
    OpcUaCommunication,
    OpcUaCommunicationConfig,
    OpcUaSubHandler,
)
from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev.base import SingleCommDevice
from hvl_ccb.dev.cube import constants
from hvl_ccb.dev.cube.constants import (
    _SupportPort,
    _T13Socket,
    _MeasurementChannel,
    _EarthingStick,
    _Door,
    _EarthingRod,
    _CubeOpcEndpoint,
    CubeStatusChangeError,
    CubeRemoteControlError,
    CubeStopError,
)
from hvl_ccb.dev.utils import Poller
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_bool, validate_number

logger = logging.getLogger(__name__)


class _BaseCubeSubscriptionHandler(OpcUaSubHandler):
    """
    OPC Subscription handler for datachange events and normal events specifically
    implemented for the BaseCube devices.
    """

    def __init__(self):
        self.alarm_status = constants._AlarmsOverview()

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
        try:
            alarm_number = constants._Alarms(node.nodeid.Identifier).number
            setattr(
                self.alarm_status, f"alarm_{alarm_number}", constants._AlarmStatus(val)
            )
            alarm_level = constants._AlarmText.get_level(alarm_number)
            if val:
                alarm_text = constants._AlarmText.get_coming_message(alarm_number)
            else:
                alarm_text = constants._AlarmText.get_going_message(alarm_number)

            alarm_log_postfix = ""
            if logger.root.level <= logging.DEBUG:
                alarm_log_postfix = f" (opc alarm {alarm_number})"  # pragma: no cover

            if alarm_level == logging.DEBUG:
                logger.debug(f"{alarm_text}{alarm_log_postfix}")
            elif alarm_level == logging.INFO:
                logger.info(f"{alarm_text}{alarm_log_postfix}")
            elif alarm_level >= logging.WARNING:
                logger.warning(f"{alarm_text}{alarm_log_postfix}")
            return
        except ValueError:
            # not any of Alarms node IDs
            pass

        id_ = node.nodeid.Identifier

        # assume a status datachange
        if id_ == str(constants._Safety.STATUS):
            new_status = str(constants.SafetyStatus(val))
            logger.info(f"Safety: {new_status}")
            return

        # assume an earthing stick status datachange
        for i in _EarthingStick._STICKS:
            if id_ in _EarthingStick("", i)._CMD_STATUS:
                new_status = str(constants.EarthingStickStatus(val))
                logger.info(f"Earthing Stick {i}: {new_status}")
                return


@configdataclass
class BaseCubeConfiguration:
    """
    Configuration dataclass for the BaseCube devices.
    """

    #: Namespace of the OPC variables, typically this is 3 (coming from Siemens)
    namespace_index: int = 3

    polling_delay_sec: Number = 5.0
    polling_interval_sec: Number = 1.0

    timeout_status_change: Number = 6
    timeout_interval: Number = 0.1

    noise_level_measurement_channel_1: Number = 100
    noise_level_measurement_channel_2: Number = 100
    noise_level_measurement_channel_3: Number = 100
    noise_level_measurement_channel_4: Number = 100

    def clean_values(self):
        if self.namespace_index < 0:
            raise ValueError(
                "Index of the OPC variables namespace needs to be a positive integer."
            )
        if self.polling_interval_sec <= 0:
            raise ValueError("Polling interval needs to be positive.")
        if self.polling_delay_sec < 0:
            raise ValueError("Polling delay needs to be not negative.")
        if self.timeout_interval <= 0:
            raise ValueError("Timeout interval for status change needs to be positive.")
        if self.timeout_status_change < 0:
            raise ValueError("Timeout for status change needs to be not negative.")
        validate_number(
            "Noise Level Measurement Channel 1",
            self.noise_level_measurement_channel_1,
            logger=logger
        )
        validate_number(
            "Noise Level Measurement Channel 2",
            self.noise_level_measurement_channel_2,
            logger=logger
        )
        validate_number(
            "Noise Level Measurement Channel 3",
            self.noise_level_measurement_channel_3,
            logger=logger
        )
        validate_number(
            "Noise Level Measurement Channel 4",
            self.noise_level_measurement_channel_4,
            logger=logger
        )


@configdataclass
class BaseCubeOpcUaCommunicationConfig(OpcUaCommunicationConfig):
    """
    Communication protocol configuration for OPC UA, specifications for the BaseCube
    devices.
    """

    #: Subscription handler for data change events
    sub_handler: OpcUaSubHandler = _BaseCubeSubscriptionHandler()
    endpoint_name: _CubeOpcEndpoint = _CubeOpcEndpoint.BASE_CUBE  # type: ignore


class BaseCubeOpcUaCommunication(OpcUaCommunication):
    """
    Communication protocol specification for BaseCube devices.
    """

    @staticmethod
    def config_cls():
        return BaseCubeOpcUaCommunicationConfig


class BaseCube(SingleCommDevice):
    """
    Base class for Cube variants.
    """

    OPC_MIN_YEAR = 1990
    OPC_MAX_YEAR = 2089

    def __init__(self, com, dev_config=None):
        """
        Constructor for BaseCube.

        :param com: the communication protocol or its configuration
        :param dev_config: the device configuration
        """

        super().__init__(com, dev_config)

        self._status_poller = Poller(
            self._spoll_handler,
            polling_delay_sec=self.config.polling_delay_sec,
            polling_interval_sec=self.config.polling_interval_sec,
        )
        self._toggle = cycle([False, True])
        self._message_len = len(constants.MessageBoard)
        self._status_board = [""] * self._message_len
        self._message_board = deque([""] * self._message_len, maxlen=self._message_len)

        # create earthing sticks
        self.earthing_stick_1 = _EarthingStick(self, 1)
        self.earthing_stick_2 = _EarthingStick(self, 2)
        self.earthing_stick_3 = _EarthingStick(self, 3)
        self.earthing_stick_4 = _EarthingStick(self, 4)
        self.earthing_stick_5 = _EarthingStick(self, 5)
        self.earthing_stick_6 = _EarthingStick(self, 6)

        # create support ports, each port has two inputs and outputs
        self.support_1 = _SupportPort(self, 1)
        self.support_2 = _SupportPort(self, 2)
        self.support_3 = _SupportPort(self, 3)
        self.support_4 = _SupportPort(self, 4)
        self.support_5 = _SupportPort(self, 5)
        self.support_6 = _SupportPort(self, 6)

        # create measurement channels
        self.measurement_ch_1 = _MeasurementChannel(
            self, 1, input_noise=self.config.noise_level_measurement_channel_1
        )
        self.measurement_ch_2 = _MeasurementChannel(
            self, 2, input_noise=self.config.noise_level_measurement_channel_2
        )
        self.measurement_ch_3 = _MeasurementChannel(
            self, 3, input_noise=self.config.noise_level_measurement_channel_3
        )
        self.measurement_ch_4 = _MeasurementChannel(
            self, 4, input_noise=self.config.noise_level_measurement_channel_4
        )

    @staticmethod
    def default_com_cls():
        return BaseCubeOpcUaCommunication

    @staticmethod
    def config_cls():
        return BaseCubeConfiguration

    def start(self) -> None:
        """
        Starts the device. Sets the root node for all OPC read and write commands to
        the Siemens PLC object node which holds all our relevant objects and variables.
        """

        logger.info("Starting Cube")
        super().start()

        logger.debug("Add monitoring nodes")
        self.com.init_monitored_nodes(
            constants._CEE16, self.config.namespace_index
        )
        # add T13 sockets
        for socket in _T13Socket._SOCKETS:
            self.com.init_monitored_nodes(
                _T13Socket(socket)._CMD, self.config.namespace_index
            )
        for io, port, contact in product(
                _SupportPort._IOS,
                _SupportPort._PORTS,
                _SupportPort._CONTACTS
        ):
            self.com.init_monitored_nodes(
                _SupportPort("", port)._cmd(io, contact),
                self.config.namespace_index
            )
        self.com.init_monitored_nodes(
            map(str, constants._Safety),  # type: ignore
            self.config.namespace_index,
        )
        self.com.init_monitored_nodes(
            str(constants._Errors.MESSAGE), self.config.namespace_index
        )
        self.com.init_monitored_nodes(
            str(constants._Errors.WARNING), self.config.namespace_index
        )
        self.com.init_monitored_nodes(
            str(constants._Errors.STOP), self.config.namespace_index
        )
        self.com.init_monitored_nodes(
            map(str, constants._Alarms), self.config.namespace_index
        )
        for i in _EarthingStick._STICKS:
            self.com.init_monitored_nodes(
                constants._EarthingStick("", i)._CMD_STATUS,
                self.config.namespace_index,
            )

        self._set_remote_control(True)
        logger.info("Finished starting")

        self._set_current_time()
        logger.debug("Sent system time to Cube.")

    def stop(self) -> None:
        """
        Stop the Cube device. Deactivates the remote control and closes the
        communication protocol.

        :raises CubeStopError: when the cube is not in the correct status
            to stop the operation
        """
        status = self._status
        if status not in constants.STOP_SAFETY_STATUSES:
            msg = (
                f"Cube needs to be in status "
                f"{' or '.join(s.name for s in constants.STOP_SAFETY_STATUSES)} "
                f"to close the connection to the device, but is in status {status.name}"
            )
            logger.error(msg)
            raise CubeStopError(msg)
        try:
            self._set_remote_control(False)
        finally:
            super().stop()
            logger.info("Stopping Cube")

    def _spoll_handler(self) -> None:
        """
        Cube poller handler; change one byte on a Cube.
        """
        self.write(constants._OpcControl.LIVE, next(self._toggle))

    def read(self, node_id: str):
        """
        Local wrapper for the OPC UA communication protocol read method.

        :param node_id: the id of the node to read.
        :return: the value of the variable
        """

        logger.debug(f"Read from node ID {node_id} ...")
        result = self.com.read(str(node_id), self.config.namespace_index)
        logger.debug(f"Read from node ID {node_id}: {result}")
        return result

    def write(self, node_id, value) -> None:
        """
        Local wrapper for the OPC UA communication protocol write method.

        :param node_id: the id of the node to write
        :param value: the value to write to the variable
        """
        logger.debug(f"Write to node ID {node_id}: {value}")
        self.com.write(str(node_id), self.config.namespace_index, value)

    @classmethod
    def datetime_to_opc(cls, time_dt: datetime) -> List[int]:
        """
        Converts python datetime format into opc format (list of 8 integers) as defined
        in the following link:
        https://support.industry.siemens.com/cs/mdm/109798671?c=133950752267&lc=de-WW
        Each byte corresponds to one list entry.
        [yy, MM, dd, hh, mm, ss, milliseconds, weekday]
        Milliseconds and Weekday are not used, as this precision / information is not
        needed.
        The conversion of the numbers is special. Each decimal number is treated as it
        would be a hex-number and then converted back to decimal.
        This is tested with the used PLC in the BaseCube.
        yy: 0 to 99 (0 -> 2000, 89 -> 2089, 90 -> 1990, 99 -> 1999)
        MM: 1 to 12
        dd: 1 to 31
        hh: 0 to 23
        mm: 0 to 59
        ss: 0 to 59

        :param time_dt: time to be converted
        :return: time in opc list format
        """

        validate_number("year", time_dt.year, (cls.OPC_MIN_YEAR, cls.OPC_MAX_YEAR), int)

        time_tuple = (
            int(str(time_dt.year)[2:]),
            time_dt.month,
            time_dt.day,
            time_dt.hour,
            time_dt.minute,
            time_dt.second,
            0,
            0,
        )
        return [int(f"0x{time_comp}", base=0) for time_comp in time_tuple]

    def _set_current_time(self) -> None:
        """
        Send current UTC time of host computer to Cube. As the time is only
        synchronized during the startup and after the polling started, the polling delay
        is added to the current time
        """
        time_opc = self.datetime_to_opc(
            datetime.utcnow() + timedelta(seconds=self.config.polling_delay_sec)
        )
        self.write(constants._OpcControl.TIME, time_opc)

    def _set_remote_control(self, state: bool) -> None:
        """
        Enable or disable remote control for the Cube. This will effectively
        display a message on the touchscreen HMI.

        :param state: desired remote control state
        :raises TypeError: when state is not of type bool
        :raises CubeRemoteControlError: when the remote control
            cannot be (de-)activated
        """
        validate_bool("state", state, logger)
        if not state and self._status not in constants.STOP_SAFETY_STATUSES:
            status = self._status
            msg = (
                f"Cube needs to be in status 'GREEN_NOT_READY' or 'GREEN_READY' "
                f"to turn off the remote control, but is in '{status.name}'"
            )
            logger.error(msg)
            raise CubeRemoteControlError(msg)
        can_write = False
        try:
            self.write(constants._OpcControl.ACTIVE, state)
            can_write = True
        finally:
            if state:
                if not can_write:
                    msg = "Remote control cannot be enabled"  # pragma: no cover
                    logger.error(msg)  # pragma: no cover
                    raise CubeRemoteControlError(msg)  # pragma: no cover
                else:
                    was_not_polling = self._status_poller.start_polling()
                    if not was_not_polling:
                        msg = "Remote control already enabled"  # pragma: no cover
                        logger.error(msg)  # pragma: no cover
                        raise CubeRemoteControlError(msg)  # pragma: no cover
            else:
                was_polling = self._status_poller.stop_polling()
                self._status_poller.wait_for_polling_result()
                if not was_polling:
                    msg = "Remote control already disabled"  # pragma: no cover
                    logger.error(msg)  # pragma: no cover
                    raise CubeRemoteControlError(msg)  # pragma: no cover

    # creates the T13 power sockets
    t13_socket_1 = _T13Socket(socket=1)
    t13_socket_2 = _T13Socket(socket=2)
    t13_socket_3 = _T13Socket(socket=3)

    @property
    def cee16_socket(self):
        """
        Read the on-state of the IEC CEE16 three-phase power socket.

        :return: the on-state of the CEE16 power socket
        """

        value = bool(self.read(constants._CEE16))
        state = "ON" if value else "OFF"
        logger.info(f"CEE 16 A Power Socket is {state}")
        return value

    @cee16_socket.setter
    def cee16_socket(self, value):
        """
        Switch the IEC CEE16 three-phase power socket on or off.

        :param value: desired on-state of the power socket
        :raises TypeError: if state is not of type bool
        """

        validate_bool("state", value, logger)

        self.write(constants._CEE16, value)
        state_str = "ON" if value else "OFF"
        logger.info(f"CEE 16 A Power Socket is switched {state_str}")

    @property
    def _status(self) -> constants.SafetyStatus:
        """
        Get the safety circuit status of the Cube.
        For internal use only, without logging

        :return: the safety status of the Cube's state machine.
        """
        return constants.SafetyStatus(self.read(constants._Safety.STATUS))

    @property
    def status(self) -> constants.SafetyStatus:
        """
        Get the safety circuit status of the Cube.
        This methods is for the user.

        :return: the safety status of the Cube's state machine.
        """

        value = self._status
        logger.info(f"Safety Status is {value.name}")
        return value

    def _switch_safety_status(
        self,
        switch: constants._SafetyStatusTransition,
        raise_state: bool = True,
    ):
        """
        Internal method to switch the safety status of the cube.
        Checks are performed if the switch can be executed.

        :param switch: indicates the transition
        :param raise_state: True will raise the state, False will lower the state
        :raise CubeStatusChangeError: if the status change was not successful or
            the status cannot be changed because the cube is in the wrong safety status
            for the queried operation
        """
        source = constants._SafetyStatusTransition(switch).source
        target = constants._SafetyStatusTransition(switch).target
        actual_status = self._status
        if raise_state and actual_status is not source:
            msg = (
                f"Cube needs to be in status '{source.name}' in order to switch "
                f"to '{target.name}', but is in '{actual_status.name}'"
            )
            logger.error(msg)
            raise CubeStatusChangeError(msg)
        elif not raise_state and actual_status is not target:
            msg = (
                f"Cube needs to be in status '{target.name}' in order to switch "
                f"to '{source.name}', but is in '{actual_status.name}'"
            )
            logger.error(msg)
            raise CubeStatusChangeError(msg)

        status = target if raise_state else source
        logger.info(f"Status of Cube will be changed to {status.name}")  # type: ignore
        self.write(switch.command, raise_state)

        start_time = time()
        while (
            self._status is not status
            and time() - start_time < self.config.timeout_status_change
        ):
            sleep(self.config.timeout_interval)
        actual_status = self._status
        if actual_status is status:
            logger.info(
                f"Status successfully changed to {status.name}."  # type: ignore
            )
        else:
            msg = (
                f"Tried to change status to {status.name}, "  # type: ignore
                f"but Cube status is {actual_status.name}"
            )
            logger.error(msg)
            raise CubeStatusChangeError(msg)

    @property
    def ready(self) -> Optional[bool]:
        """
        Indicates if 'ready' is activated. 'ready' means locket safety circuit,
        red lamps, but high voltage still off.

        :return: `True` if ready is activated (RED_READY),
            `False` if ready is deactivated (GREEN_READY),
            `None` otherwise
        """
        status = self.status
        if status == constants.SafetyStatus.RED_READY:
            return True
        elif status == constants.SafetyStatus.GREEN_READY:
            return False
        else:
            return None

    @ready.setter
    def ready(self, state: bool) -> None:
        """
        Set ready state. Ready means locket safety circuit, red lamps, but high voltage
        still off.

        :param state: set ready state
        :raises CubeStatusChangeError: if `state=True` and cube is not in GREEN_READY or
            if `state=False` and cube is not in RED_READY
        """
        validate_bool("state", state, logger)
        self._switch_safety_status(
            switch=cast(
                constants._SafetyStatusTransition,
                constants._SafetyStatusTransition.SWITCH_TO_READY,
            ),
            raise_state=state,
        )

    @property
    def operate(self) -> Optional[bool]:
        """
        Indicates if 'operate' is activated. 'operate' means locket safety circuit,
        red lamps, high voltage on and locked safety switches.

        :return: `True` if operate is activated (RED_OPERATE),
            `False` if ready is deactivated (RED_READY),
            `None` otherwise
        """
        status = self.status
        if status == constants.SafetyStatus.RED_OPERATE:
            return True
        elif status == constants.SafetyStatus.RED_READY:
            return False
        else:
            return None

    @operate.setter
    def operate(self, state: bool) -> None:
        """
        Set operate state. This will turn on the high
        voltage and close the safety switches.

        :param state: set operate state
        :raises CubeStatusChangeError: if `state=True` and cube is not in RED_READY or
            if `state=False` and cube is not in RED_OPERATE
        """
        validate_bool("state", state, logger)
        self._switch_safety_status(
            switch=cast(
                constants._SafetyStatusTransition,
                constants._SafetyStatusTransition.SWITCH_TO_OPERATE,
            ),
            raise_state=state,
        )

    @property
    def breakdown_detection_active(self) -> bool:
        """
        Get the state of the breakdown detection functionality. Returns True if it is
        enabled, False otherwise.

        :return: state of the breakdown detection functionality
        """

        value = self.read(constants._BreakdownDetection.ACTIVATED)
        status = "" if value else "NOT "
        logger.info(f"Breakdown Detection Unit is {status}activated")
        return value

    @property
    def breakdown_detection_triggered(self) -> bool:
        """
        See if breakdown detection unit has been triggered. Returns True if it is
        triggered, False otherwise.

        :return: trigger status of the breakdown detection unit
        """
        value = self.read(constants._BreakdownDetection.TRIGGERED)
        status = "" if value else "NOT "
        logger.info(f"Breakdown Detection Unit is {status}triggered")
        return value

    def breakdown_detection_reset(self) -> None:
        """
        Reset the breakdown detection circuitry so that it is ready
        to detect breakdowns again.
        """

        self.write(constants._BreakdownDetection.RESET, True)
        sleep(0.1)
        self.write(constants._BreakdownDetection.RESET, False)
        logger.info("The Breakdown Detection Unit is reset")

    def quit_error(self) -> None:
        """
        Quits errors that are active on the Cube.
        """

        logger.info("Quit Errors of Cube")
        self.write(constants._Errors.QUIT, True)
        sleep(0.1)
        self.write(constants._Errors.QUIT, False)

    # create doors
    door_1_status = _Door(1, "door status")
    door_2_status = _Door(2, "door status")
    door_3_status = _Door(3, "door status")

    # create earthing rods
    earthing_rod_1_status = _EarthingRod(1, "earthing rod status")
    earthing_rod_2_status = _EarthingRod(2, "earthing rod status")
    earthing_rod_3_status = _EarthingRod(3, "earthing rod status")

    def set_status_board(
        self,
        msgs: List[str],
        pos: List[int] = None,
        clear_board: bool = True,
        display_board: bool = True,
    ) -> None:
        """
        Sets and displays a status board. The messages and the position of the message
        can be defined.

        :param msgs: list of strings
        :param pos: list of integers [0...14]
        :param clear_board: clear unspecified lines if `True` (default), keep otherwise
        :param display_board: display new status board if `True` (default)
        :raises ValueError: if there are too many messages or the positions indices are
            invalid.
        """
        # validate inputs
        if len(msgs) > self._message_len:
            raise ValueError(
                f"Too many message: {len(msgs)} given, "
                f"max. {self._message_len} allowed."
            )
        if pos and not all(0 < p < self._message_len for p in pos):
            raise ValueError(f"Messages positions out of 0...{self._message_len} range")

        if clear_board:
            self._status_board = [""] * self._message_len

        # update status board
        if not pos:
            pos = list(range(len(msgs)))
        for num, msg in zip(pos, msgs):
            self._status_board[num] = msg
        if display_board:
            self.display_status_board()

    def display_status_board(self) -> None:
        """
        Display status board.
        """

        self._display_messages(self._status_board)
        logger.info("Cube HMI is now displaying the Status Board")

    def set_message_board(self, msgs: List[str], display_board: bool = True) -> None:
        """
        Fills messages into message board that display that 15 newest messages with
        a timestamp.

        :param msgs: list of strings
        :param display_board: display 15 newest messages if `True` (default)
        :raises ValueError: if there are too many messages or the positions indices are
            invalid.
        """
        # validate inputs
        if len(msgs) > self._message_len:
            raise ValueError(
                f"Too many message: {len(msgs)} given, "
                f"max. {self._message_len} allowed."
            )

        timestamp = datetime.now().time().strftime("%H:%M:%S")
        # append messages in the same order as given, not reversed
        self._message_board.extendleft(f"{timestamp}: {msg}" for msg in reversed(msgs))

        if display_board:
            self.display_message_board()

    def display_message_board(self) -> None:
        """
        Display 15 newest messages
        """

        self._display_messages(self._message_board)
        logger.info("Cube HMI is now displaying the Message Board")

    def _display_messages(self, messages: Sequence[str]) -> None:
        """
        Display given messages on message board

        :param messages: sequence of messages to display
        """
        # Note: cannot zip(constants.MessageBoard, messages) as enum instances are
        #       sorted by name, hence after after `line_1` comes `line_10`, not `line_2`
        for n, msg in enumerate(messages):
            line = constants.MessageBoard.line(n + 1)
            self.write(line, msg)

    def active_alarms(self, human_readable: bool = True) -> List[Union[int, str]]:
        """
        Displays all active alarms / messages.

        :param human_readable: `True` for human readable message,
            `False` for corresponding integer
        :return: list with active alarms
        """
        validate_bool("human_readable", human_readable, logger=logger)
        active_alarms = []
        for i in constants._Alarms.range():
            if getattr(self._com.config.sub_handler.alarm_status, f"alarm_{i}"):
                if human_readable:
                    i = constants._AlarmText.get_coming_message(i)
                active_alarms.append(i)
        return active_alarms
