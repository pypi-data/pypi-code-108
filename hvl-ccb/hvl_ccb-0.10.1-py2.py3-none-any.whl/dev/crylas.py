#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device classes for a CryLas pulsed laser controller and a CryLas laser attenuator,
using serial communication.

There are three modes of operation for the laser
1. Laser-internal hardware trigger (default): fixed to 20 Hz and max energy per pulse.
2. Laser-internal software trigger (for diagnosis only).
3. External trigger: required for arbitrary pulse energy or repetition rate. Switch to
"external" on the front panel of laser controller for using option 3.

After switching on the laser with laser_on(), the system must stabilize
for some minutes. Do not apply abrupt changes of pulse energy or repetition rate.

Manufacturer homepage:
https://www.crylas.de/products/pulsed_laser.html
"""

import logging
import math
import re
import time
from datetime import datetime
from threading import Event
from typing import Union, Tuple, Optional, Callable

from aenum import Enum, IntEnum

from .base import SingleCommDevice, DeviceException
from .utils import Poller
from ..comm import SerialCommunication, SerialCommunicationConfig
from ..comm.serial import (
    SerialCommunicationParity,
    SerialCommunicationStopbits,
    SerialCommunicationBytesize,
)
from ..configuration import configdataclass
from ..utils.typing import Number

logger = logging.getLogger(__name__)


@configdataclass
class CryLasLaserSerialCommunicationConfig(SerialCommunicationConfig):
    #: Baudrate for CryLas laser is 19200 baud
    baudrate: int = 19200

    #: CryLas laser does not use parity
    parity: Union[str, SerialCommunicationParity] = SerialCommunicationParity.NONE

    #: CryLas laser uses one stop bit
    stopbits: Union[int, SerialCommunicationStopbits] = SerialCommunicationStopbits.ONE

    #: One byte is eight bits long
    bytesize: Union[
        int, SerialCommunicationBytesize
    ] = SerialCommunicationBytesize.EIGHTBITS

    #: The terminator is LF
    terminator: bytes = b"\n"

    #: use 10 seconds timeout as default (a long timeout is needed!)
    timeout: Number = 10


class CryLasLaserSerialCommunication(SerialCommunication):
    """
    Specific communication protocol implementation for the CryLas laser controller.
    Already predefines device-specific protocol parameters in config.
    """

    @staticmethod
    def config_cls():
        return CryLasLaserSerialCommunicationConfig

    READ_TEXT_SKIP_PREFIXES = (">", "MODE:")
    """Prefixes of lines that are skipped when read from the serial port."""

    def read(
        self,
    ) -> str:
        """
        Read first line of text from the serial port that does not start with any of
        `self.READ_TEXT_SKIP_PREFIXES`.

        :return: String read from the serial port; `''` if there was nothing to read.
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        with self.access_lock:
            line = super().read()
            while line.startswith(self.READ_TEXT_SKIP_PREFIXES):
                logger.debug(f'Laser com: "{line.rstrip()}" SKIPPED')
                line = super().read_text()
            logger.debug(f'Laser com: "{line.rstrip()}"')
            return line

    def query(self, cmd: str, prefix: str, post_cmd: str = None) -> str:
        """
        Send a command, then read the com until a line starting with prefix,
        or an empty line, is found. Returns the line in question.

        :param cmd: query message to send to the device
        :param prefix: start of the line to look for in the device answer
        :param post_cmd: optional additional command to send after the query
        :return: line in question as a string
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        # TODO: Make use of SyncCommunicationProtocol

        with self.access_lock:
            # send the command
            self.write(cmd)
            # read the com until the prefix or an empty line is found
            line = self.read().strip()
            while line and not line.startswith(prefix):
                line = self.read().strip()
            if post_cmd is not None:
                # send an optional post-command message to send to the device
                self.write(post_cmd)
            return line

    def query_all(self, cmd: str, prefix: str):
        """
        Send a command, then read the com until a line starting with prefix,
        or an empty line, is found. Returns a list of successive lines starting with
        prefix.

        :param cmd: query message to send to the device
        :param prefix: start of the line to look for in the device answer
        :return: line in question as a string
        :raises SerialCommunicationIOError: when communication port is not opened
        """
        # TODO: Make use of SyncCommunicationProtocol

        with self.access_lock:
            # send the command
            self.write(cmd)
            # read the com until the prefix or an empty line is found
            line = self.read().strip()
            while line and not line.startswith(prefix):
                line = self.read().strip()
            answer = []
            while line.startswith(prefix):
                answer.append(line)
                line = self.read().strip()
            return answer


class CryLasLaserShutterStatus(Enum):
    """
    Status of the CryLas laser shutter
    """

    CLOSED = 0
    OPENED = 1


@configdataclass
class CryLasLaserConfig:
    """
    Device configuration dataclass for the CryLas laser controller.
    """

    # status of the shutter
    ShutterStatus = CryLasLaserShutterStatus

    # calibration factor for the pulse energy
    calibration_factor: Number = 4.35

    # polling period (s) to check back on the laser status if not ready
    # it should be longer than the communication timeout
    polling_period: Union[int, float] = 12

    # timeout (s) when polling the laser status, CryLasLaserError is raised on timeout
    polling_timeout: Number = 300

    # automatically turn on the laser when ready
    auto_laser_on: bool = True

    # status of the shutter to be set on start
    init_shutter_status: Union[
        int, CryLasLaserShutterStatus
    ] = CryLasLaserShutterStatus.CLOSED

    def clean_values(self):
        if self.calibration_factor <= 0:
            raise ValueError("The calibration factor should be positive.")
        if self.polling_period <= 0:
            raise ValueError("The polling period should be positive.")
        if self.polling_timeout <= 0:
            raise ValueError("The polling timeout should be positive.")
        self.force_value(
            "init_shutter_status", self.ShutterStatus(self.init_shutter_status)
        )


class CryLasLaserPoller(Poller):
    """
    Poller class for polling the laser status until the laser is ready.

    :raises CryLasLaserError: if the timeout is reached before the laser is ready
    :raises SerialCommunicationIOError: when communication port is closed.
    """

    def __init__(
        self,
        spoll_handler: Callable,
        check_handler: Callable,
        check_laser_status_handler: Callable,
        polling_delay_sec: Number = 0,
        polling_interval_sec: Number = 1,
        polling_timeout_sec: Optional[Number] = None,
    ):
        """
        Initialize the polling helper.

        :param spoll_handler: Polling function.
        :param check_handler: Check polling results.
        :param check_laser_status_handler: Check laser status.
        :param polling_delay_sec: Delay before starting the polling, in seconds.
        :param polling_interval_sec: Polling interval, in seconds.
        """
        super().__init__(
            spoll_handler, polling_delay_sec, polling_interval_sec, polling_timeout_sec
        )

        self._check_handler = check_handler
        self._check_laser_status_handler = check_laser_status_handler

    def _if_poll_again(
        self, stop_event: Event, delay_sec: Number, stop_time: Optional[Number]
    ) -> bool:
        """
        Check if to poll again.

        :param stop_event: Polling stop event.
        :param delay_sec: Delay time (in seconds).
        :param stop_time: Absolute stop time.
        :return: `True` if another polling handler call is due, `False` otherwise.
        """
        if_poll_again = super()._if_poll_again(stop_event, delay_sec, stop_time)
        is_laser_ready = self._check_laser_status_handler()

        return if_poll_again and not is_laser_ready

    def _poll_until_stop_or_timeout(self, stop_event: Event) -> Optional[object]:
        """
        Thread for polling until stopped, timed-out or the laser is ready.

        :param stop_event: Event used to stop the polling
        :return: Last result of the polling function call
        """
        last_result = super()._poll_until_stop_or_timeout(stop_event)

        if stop_event.wait(0):
            logger.info(f"[{datetime.now()}] Polling status: ... STOPPED")
            return last_result
        else:
            self._check_handler()

        return last_result


class CryLasLaser(SingleCommDevice):
    """
    CryLas laser controller device class.
    """

    class LaserStatus(Enum):
        """
        Status of the CryLas laser
        """

        UNREADY_INACTIVE = 0
        READY_INACTIVE = 1
        READY_ACTIVE = 2

        @property
        def is_ready(self):
            return self is not CryLasLaser.LaserStatus.UNREADY_INACTIVE

        @property
        def is_inactive(self):
            return self is not CryLasLaser.LaserStatus.READY_ACTIVE

    # status of the shutter
    ShutterStatus = CryLasLaserShutterStatus

    class AnswersShutter(Enum):
        """
        Standard answers of the CryLas laser controller to `'Shutter'` command passed
        via `com`.
        """

        OPENED = "Shutter aktiv"
        CLOSED = "Shutter inaktiv"

    class AnswersStatus(Enum):
        """
        Standard answers of the CryLas laser controller to `'STATUS'` command passed
        via `com`.
        """

        TEC1 = "STATUS: TEC1 Regulation ok"
        TEC2 = "STATUS: TEC2 Regulation ok"
        HEAD = "STATUS: Head ok"
        READY = "STATUS: System ready"
        ACTIVE = "STATUS: Laser active"
        INACTIVE = "STATUS: Laser inactive"

    class RepetitionRates(IntEnum, init="value send_value"):  # type: ignore
        """
        Repetition rates for the internal software trigger in Hz
        """

        HARDWARE = 0, 0  # software trigger is disabled, hardware trigger is used
        # instead (hardware trigger may be internal or external).
        SOFTWARE_INTERNAL_TEN = 10, 1
        SOFTWARE_INTERNAL_TWENTY = 20, 2
        SOFTWARE_INTERNAL_SIXTY = 60, 3

    def __init__(self, com, dev_config=None):

        # Call superclass constructor
        super().__init__(com, dev_config)

        # laser status
        self.laser_status = self.LaserStatus.UNREADY_INACTIVE

        # shutter status
        self.shutter_status = None

        # command repetition rate
        self.repetition_rate = None

        # command pulse energy (micro joule)
        self._target_pulse_energy = None

        # thread that polls the laser status until it is ready
        self._status_poller = None

    @property
    def target_pulse_energy(self):
        return self._target_pulse_energy

    @staticmethod
    def default_com_cls():
        return CryLasLaserSerialCommunication

    @staticmethod
    def config_cls():
        return CryLasLaserConfig

    def start(self) -> None:
        """
        Opens the communication protocol and configures the device.

        :raises SerialCommunicationIOError: when communication port cannot be opened
        """

        logger.info("Starting device " + str(self))

        # open the com
        super().start()

        # set the init shutter status
        self.set_init_shutter_status()
        # check if the laser is ready to be turned on
        self.update_laser_status()
        if not self.laser_status.is_ready:
            logger.info("Laser not ready yet.")
            # optionally, block execution until laser is ready
            if self.config.auto_laser_on and not self._is_polling():
                self._start_polling()
        elif self.config.auto_laser_on:
            # turn on the laser
            self.laser_on()

    def _start_polling(self):
        """
        Start polling laser status.
        """
        logger.info("Start polling laser status.")
        self._status_poller = CryLasLaserPoller(
            spoll_handler=self.update_laser_status,
            check_handler=self._after_polling_check_status,
            check_laser_status_handler=self._check_laser_status_handler,
            polling_delay_sec=self.config.polling_period,
            polling_interval_sec=self.config.polling_period,
            polling_timeout_sec=self.config.polling_timeout,
        )
        self._status_poller.start_polling()

    def _check_laser_status_handler(self) -> bool:
        """
        Checks whether the laser status is ready.
        """
        return self.laser_status.is_ready

    def _after_polling_check_status(self) -> None:
        """
        Thread for polling the laser status until the laser is ready.

        :raises CryLasLaserError: if the timeout is reached before the laser is ready
        :raises SerialCommunicationIOError: when communication port is closed.
        """

        if not self.laser_status.is_ready:
            err_msg = "Laser is not yet ready but status polling timed out."
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)

        logger.info(f"[{datetime.now()}] Polling status: ... DONE")
        if self.config.auto_laser_on:
            self.laser_on()

    def _wait_for_polling_result(self):
        """
        Wait for until polling function returns a result as well as any exception that
        might have been raised within a thread.

        :return: polling function result
        :raises: polling function errors
        """
        return self._status_poller.wait_for_polling_result()

    def _stop_polling(self):
        """
        Stop polling laser status.

        :return: polling function result
        :raises: polling function errors
        """
        # use the event to stop the thread
        logger.info("Stop polling laser status.")
        self._status_poller.stop_polling()
        return self._wait_for_polling_result()

    def _is_polling(self) -> bool:
        """
        Check if device status is being polled.

        :return: `True` when polling thread is set and alive
        """
        return self._status_poller is not None and self._status_poller.is_polling()

    def wait_until_ready(self) -> None:
        """
        Block execution until the laser is ready

        :raises CryLasLaserError: if the polling thread stops before the laser is ready
        """

        if not self.laser_status.is_ready:
            if not self._is_polling():
                self._start_polling()
            logger.info("Waiting until the laser is ready...")
            self._wait_for_polling_result()
        else:
            logger.info("No need waiting, the laser is already ready.")

    def stop(self) -> None:
        """
        Stops the device and closes the communication protocol.

        :raises SerialCommunicationIOError: if com port is closed unexpectedly
        :raises CryLasLaserError: if laser_off() or close_shutter() fail
        """

        if self.com.is_open:
            # turn off the laser
            self.laser_off()
            # close the laser shutter
            self.close_shutter()
            # cancel the polling thread in case still running
            if self._is_polling():
                self._stop_polling()
                logger.info("The laser polling thread was stopped.")
            # close the com
            super().stop()
        else:
            logger.warning("Could not turn off the laser, com was already closed.")

    def update_laser_status(self) -> None:
        """
        Update the laser status to `LaserStatus.NOT_READY` or `LaserStatus.INACTIVE` or
        `LaserStatus.ACTIVE`.

        Note: laser never explicitly says that it is not ready  (
        `LaserStatus.NOT_READY`) in response to `'STATUS'` command. It only says
        that it is ready (heated-up and implicitly inactive/off) or active (on). If
        it's not either of these then the answer is `Answers.HEAD`. Moreover,
        the only time the laser explicitly says that its status is inactive (
        `Answers.INACTIVE`) is after issuing a 'LASER OFF' command.

        :raises SerialCommunicationIOError: when communication port is not opened
        """

        # query the status
        answer_list = self.com.query_all("STATUS", "STATUS:")
        # analyze the answer
        if not answer_list:
            err_msg = "Command to query the laser status did not return an answer."
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)
        else:
            # at least one line in answer_list
            for line in answer_list:
                answer = self.AnswersStatus(line)
                if answer in (
                    self.AnswersStatus.TEC1,
                    self.AnswersStatus.TEC2,
                    self.AnswersStatus.HEAD,
                ):
                    new_status = self.LaserStatus.UNREADY_INACTIVE
                    info_msg = "The laser is not ready."
                elif answer is self.AnswersStatus.READY:
                    new_status = self.LaserStatus.READY_INACTIVE
                    info_msg = "The laser is ready."
                elif answer is self.AnswersStatus.ACTIVE:
                    new_status = self.LaserStatus.READY_ACTIVE
                    info_msg = "The laser is on."
                else:
                    err_msg = f'Unexpected "STATUS" query response {answer.value}.'
                    logger.error(err_msg)
                    raise CryLasLaserError(err_msg)
            self.laser_status = new_status
            logger.info(info_msg)

    def update_shutter_status(self) -> None:
        """
        Update the shutter status (OPENED or CLOSED)

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        # query the status
        answer = self.com.query("Shutter", "Shutter")
        # analyse the answer
        if not answer:
            err_msg = "Command to query the shutter status did not return an answer."
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)
        else:
            answer = self.AnswersShutter(answer)
            if answer is self.AnswersShutter.CLOSED:
                logger.info("The laser shutter is currently CLOSED.")
                self.shutter_status = self.ShutterStatus.CLOSED
            elif answer is self.AnswersShutter.OPENED:
                logger.info("The laser shutter is currently OPENED.")
                self.shutter_status = self.ShutterStatus.OPENED

    def update_repetition_rate(self) -> None:
        """
        Query the laser repetition rate.

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        # query the repetition rate
        answer = self.com.query("BOO IP", "Impuls=")
        # analyse the answer
        if not answer:
            err_msg = "Querying the repetition rate did not return an answer."
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)
        elif answer == "Impuls=disabled, extern Trigger":
            logger.info(
                "The laser is using a hardware trigger "
                "(may be internal or external)."
            )
            self.repetition_rate = self.RepetitionRates.HARDWARE
        elif answer.startswith("Impuls=enabled"):
            match = re.search(r"\d+", answer)
            if match is None:
                err_msg = (
                    f"Expected rate integer to follow 'Impuls=enabled' answer "
                    f"in {answer} while querying the repetition."
                )
                logger.error(err_msg)
                raise CryLasLaserError(err_msg)
            rate = int(match.group(0))
            self.repetition_rate = self.RepetitionRates(rate)
            logger.info(
                "The laser is using the internal " f"software trigger at {rate} Hz."
            )

    def update_target_pulse_energy(self) -> None:
        """
        Query the laser pulse energy.

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        # query the repetition rate
        answer = self.com.query("BOO SE", "PD-Sollwert=")
        # analyse the answer
        if not answer:
            err_msg = (
                "Command to query the target pulse energy did not return an answer."
            )
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)
        else:
            current_value = int(answer.split("=")[1])
            current_energy = int(current_value * self.config.calibration_factor / 1000)
            # update the pulse energy attribute
            self._target_pulse_energy = current_energy
            logger.info(f"The target pulse energy is {current_energy} uJ.")

    def laser_on(self) -> None:
        """
        Turn the laser on.

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserNotReadyError: if the laser is not ready to be turned on
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        if not self.laser_status.is_ready:
            raise CryLasLaserNotReadyError("Laser not ready, cannot be turned on yet.")
        else:
            # send the command
            answer = self.com.query("LASER ON", "STATUS: Laser")
            # analyse the answer
            if not answer or self.AnswersStatus(answer) != self.AnswersStatus.ACTIVE:
                if not self.laser_status.is_inactive:
                    logger.info("Laser is already on.")
                else:
                    err_msg = (
                        f"Command to turn on the laser "
                        f"{'failed' if answer else 'did not return an answer'}."
                    )
                    logger.error(err_msg)
                    raise CryLasLaserError(err_msg)
            else:
                self.laser_status = self.LaserStatus.READY_ACTIVE
                logger.info("Laser is turned on.")

    def laser_off(self) -> None:
        """
        Turn the laser off.

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        # send the command
        answer = self.com.query("LASER OFF", "STATUS: Laser")
        # analyse the answer
        if not answer or self.AnswersStatus(answer) != self.AnswersStatus.INACTIVE:
            if self.laser_status.is_inactive:
                logger.info("Laser is already off.")
            else:
                err_msg = (
                    f"Command to turn off the laser "
                    f"{'failed' if answer else 'did not return an answer'}."
                )
                logger.error(err_msg)
                raise CryLasLaserError(err_msg)
        else:
            self.laser_status = self.LaserStatus.READY_INACTIVE
            logger.info("Laser is turned off.")

    def open_shutter(self) -> None:
        """
        Open the laser shutter.

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        # send the command
        answer = self.com.query(
            f"Shutter {self.config.ShutterStatus.OPENED.value}", "Shutter"
        )
        # analyse the answer
        if not answer or self.AnswersShutter(answer) != self.AnswersShutter.OPENED:
            err_msg = (
                f"Opening laser shutter "
                f"{'failed' if answer else 'did not return an answer'}."
            )
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)
        else:
            logger.info("Opening laser shutter succeeded.")
            self.shutter_status = self.ShutterStatus.OPENED

    def close_shutter(self) -> None:
        """
        Close the laser shutter.

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        # send the command
        answer = self.com.query(
            f"Shutter {self.config.ShutterStatus.CLOSED.value}", "Shutter"
        )
        # analyse the answer
        if not answer or self.AnswersShutter(answer) != self.AnswersShutter.CLOSED:
            err_msg = (
                f"Closing laser shutter "
                f"{'failed' if answer else 'did not return an answer'}."
            )
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)
        else:
            logger.info("Closing laser shutter succeeded.")
            self.shutter_status = self.ShutterStatus.CLOSED

    def set_init_shutter_status(self) -> None:
        """
        Open or close the shutter, to match the configured shutter_status.

        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        self.update_shutter_status()
        if self.config.init_shutter_status != self.shutter_status:
            if self.config.init_shutter_status == self.ShutterStatus.CLOSED:
                self.close_shutter()
            elif self.config.init_shutter_status == self.ShutterStatus.OPENED:
                self.open_shutter()

    def get_pulse_energy_and_rate(self) -> Tuple[int, int]:
        """
        Use the debug mode, return the measured pulse energy and rate.

        :return: (energy in micro joule, rate in Hz)
        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if the device does not answer the query
        """

        # send the command (enter the debug mode)
        answer = self.com.query("DB1", "IST:", "DB0")
        if not answer:
            err_msg = "Command to find laser energy and rate did not return an answer."
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)
        else:
            # the answer should look like 'IST: LDTemp=x, NLOTemp=x, CaseTemp=x,
            # PD=x, D_I= x, freq=x, LDE=x, RegOFF=x' where x are integers
            # find the values of interest
            values = re.findall(r"\d+", answer)
            energy = int(int(values[3]) * self.config.calibration_factor / 1000)
            rate = int(values[5])
            logger.info(f"Laser energy: {energy} uJ, repetition rate: {rate} Hz.")
            return energy, rate

    def set_repetition_rate(self, rate: Union[int, RepetitionRates]) -> None:
        """
        Sets the repetition rate of the internal software trigger.

        :param rate: frequency (Hz) as an integer
        :raises ValueError: if rate is not an accepted value in RepetitionRates Enum
        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if success is not confirmed by the device
        """

        # check if the value is ok
        if not isinstance(rate, self.RepetitionRates):
            try:
                rate = self.RepetitionRates(rate)
            except ValueError as e:
                logger.error(str(e), exc_info=e)
                raise e
        # send the corresponding value to the controller
        answer = self.com.query(f"BOO IP{rate.send_value}", "Impuls=")
        # check the success of the command
        if rate != self.RepetitionRates.HARDWARE:
            # check whether the expected answer is obtained
            if answer != f"Impuls=enabled {rate}Hz":
                err_msg = (
                    f"Setting the repetition rate failed. Controller answered:"
                    f" {answer}."
                )
                logger.error(err_msg)
                raise CryLasLaserError(err_msg)
            else:
                logger.info(f"Laser internal software trigger set to {rate.value} Hz")
        else:
            # For the internal hardware trigger rate, there is no way to check success
            logger.info("Using laser internal hardware trigger.")
        # update the repetition rate attribute
        self.repetition_rate = rate

    def set_pulse_energy(self, energy: int) -> None:
        """
        Sets the energy of pulses (works only with external hardware trigger).
        Proceed with small energy steps, or the regulation may fail.

        :param energy: energy in micro joule
        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasLaserError: if the device does not confirm success
        """

        # convert the input value into the required command value
        command_value = int(energy * 1000 / self.config.calibration_factor)
        # send the command
        answer = self.com.query(f"BOO SE {command_value}", "PD-Sollwert=")
        # analyse the answer
        if not answer:
            err_msg = "Command to set the pulse energy did not return an answer."
            logger.error(err_msg)
            raise CryLasLaserError(err_msg)
        else:
            current_value = int(answer.split("=")[1])
            current_energy = int(current_value * self.config.calibration_factor / 1000)
            # update the pulse energy attribute
            self._target_pulse_energy = current_energy
            if current_value != command_value:
                message = (
                    f"Command to set the pulse energy failed. "
                    f"The pulse energy is currently set to {current_energy} "
                    f"micro joule. Setting a different value is only possible "
                    f"when using an external hardware trigger."
                )
                logger.error(message)
                raise CryLasLaserError(message)
            else:
                logger.info(f"Successfully set pulse energy to {energy}")


class CryLasLaserError(DeviceException):
    """
    General error with the CryLas Laser.
    """

    pass


class CryLasLaserNotReadyError(CryLasLaserError):
    """
    Error when trying to turn on the CryLas Laser before it is ready.
    """

    pass


@configdataclass
class CryLasAttenuatorSerialCommunicationConfig(SerialCommunicationConfig):
    #: Baudrate for CryLas attenuator is 9600 baud
    baudrate: int = 9600

    #: CryLas attenuator does not use parity
    parity: Union[str, SerialCommunicationParity] = SerialCommunicationParity.NONE

    #: CryLas attenuator uses one stop bit
    stopbits: Union[int, SerialCommunicationStopbits] = SerialCommunicationStopbits.ONE

    #: One byte is eight bits long
    bytesize: Union[
        int, SerialCommunicationBytesize
    ] = SerialCommunicationBytesize.EIGHTBITS

    #: No terminator
    terminator: bytes = b""

    #: use 3 seconds timeout as default
    timeout: Number = 3


class CryLasAttenuatorSerialCommunication(SerialCommunication):
    """
    Specific communication protocol implementation for
    the CryLas attenuator.
    Already predefines device-specific protocol parameters in config.
    """

    @staticmethod
    def config_cls():
        return CryLasAttenuatorSerialCommunicationConfig


@configdataclass
class CryLasAttenuatorConfig:
    """
    Device configuration dataclass for CryLas attenuator.
    """

    # initial/default attenuation value which is set on start()
    init_attenuation: Number = 0
    response_sleep_time: Number = 1

    def clean_values(self):
        if not 0 <= self.init_attenuation <= 100:
            raise ValueError("Attenuation should be " "between 0 and 100 included.")
        if self.response_sleep_time <= 0:
            raise ValueError("Response sleep time should be positive.")


class CryLasAttenuator(SingleCommDevice):
    """
    Device class for the CryLas laser attenuator.
    """

    def __init__(self, com, dev_config=None):
        # Call superclass constructor
        super().__init__(com, dev_config)

        # attenuation of the laser light in percent (not determined yet)
        self._attenuation = None

    @staticmethod
    def default_com_cls():
        return CryLasAttenuatorSerialCommunication

    @staticmethod
    def config_cls():
        return CryLasAttenuatorConfig

    @property
    def attenuation(self) -> Number:
        return self._attenuation

    @property
    def transmission(self) -> Number:
        return 100 - self._attenuation

    def start(self) -> None:
        """
        Open the com, apply the config value 'init_attenuation'

        :raises SerialCommunicationIOError: when communication port cannot be opened
        """

        super().start()
        self.set_init_attenuation()

    def set_init_attenuation(self):
        """
        Sets the attenuation to its configured initial/default value

        :raises SerialCommunicationIOError: when communication port is not opened
        """

        self.set_attenuation(self.config.init_attenuation)

    def set_attenuation(self, percent: Number) -> None:
        """
        Set the percentage of attenuated light (inverse of set_transmission).
        :param percent: percentage of attenuation, number between 0 and 100
        :raises ValueError: if param percent not between 0 and 100
        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasAttenuatorError: if the device does not confirm success
        """

        if not 0 <= percent <= 100:
            raise ValueError("Attenuation should be between 0 and 100 included.")
        else:
            pulse = int(math.asin((50 - percent) * 0.02) * 536.5 + 6000)
            prepulse = pulse - 400
            # prepare the values to send with the motor protocol
            lsb = prepulse % 128
            msb = math.floor(prepulse / 128)
            # send the values
            self.com.write_bytes(bytes([132, 0, lsb, msb]))
            time.sleep(self.config.response_sleep_time)
            lsb = pulse % 128
            msb = math.floor(pulse / 128)
            self.com.write_bytes(bytes([132, 0, lsb, msb]))
            time.sleep(self.config.response_sleep_time / 10)
            self.com.write_bytes(bytes([161]))
            time.sleep(self.config.response_sleep_time / 10)
            b1 = self.com.read_single_bytes()
            b2 = self.com.read_single_bytes()
            logger.debug(f"b1 = {b1}, b2 = {b2}")
            if b1 != b"\x00" or b2 != b"\x00":
                err_msg = f"Setting laser attenuation to {percent} percents failed."
                logger.error(err_msg)
                raise CryLasAttenuatorError(err_msg)
            else:
                logger.info(
                    f"Successfully set laser attenuation to {percent} Cpercents."
                )
                self._attenuation = percent

    def set_transmission(self, percent: Number) -> None:
        """
        Set the percentage of transmitted light (inverse of set_attenuation).
        :param percent: percentage of transmitted light
        :raises ValueError: if param percent not between 0 and 100
        :raises SerialCommunicationIOError: when communication port is not opened
        :raises CryLasAttenuatorError: if the device does not confirm success
        """

        self.set_attenuation(100 - percent)


class CryLasAttenuatorError(DeviceException):
    """
    General error with the CryLas Attenuator.
    """

    pass
