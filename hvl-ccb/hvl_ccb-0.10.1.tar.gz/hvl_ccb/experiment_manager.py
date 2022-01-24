#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Main module containing the top level ExperimentManager class.
Inherit from this class to implement your own experiment functionality in another
project and it will help you start, stop and manage your devices.
"""

import logging
from enum import Enum
from typing import Dict

from .dev import Device, DeviceSequenceMixin

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """
    Enumeration for the experiment status
    """

    INITIALIZING = -1
    INITIALIZED = 0
    STARTING = 1
    RUNNING = 2
    FINISHING = 3
    FINISHED = 4
    ERROR = 5


class ExperimentError(Exception):
    """
    Exception to indicate that the current status of the experiment manager is on
    ERROR and thus no operations can be made until reset.
    """


class ExperimentManager(DeviceSequenceMixin):
    """
    Experiment Manager can start and stop communication protocols and devices.
    It provides methods to queue commands to
    devices and collect results.
    """

    def __new__(cls, *args, **kwargs) -> "ExperimentManager":
        """
        Construct a new `ExperimentManager` instance.

        :param args: `__init__` arguments
        :param kwargs: `__init__` keyword arguments
        :return: `ExperimentManager` with status set to `ExperimentStatus.INITIALIZING`.
        """
        obj = super().__new__(cls)
        # experiment manager status
        obj._status = ExperimentStatus.INITIALIZING
        return obj

    def __init__(self, devices: Dict[str, Device]) -> None:
        """
        Initialize `ExperimentManager`. Takes a dictionary of instantiated devices
        and initializes the experiment status to `ExperimentStatus.INITIALIZED`.

        :param devices: Devices sequenced in the experiment.
        """
        super().__init__(devices)

        self._change_status(ExperimentStatus.INITIALIZED)

    def _change_status(self, new_status: ExperimentStatus) -> None:
        """
        Change the status of this experiment manager to a new value. Includes logging.

        :param new_status: is the Enum of the new experiment status.
        """

        if new_status is not self._status:
            log_msg = f"Experiment Status: {new_status} {new_status.name}"
            # new status is different, log
            if new_status is ExperimentStatus.ERROR:
                logger.error(log_msg)
            else:
                logger.info(log_msg)
            self._status: ExperimentStatus = new_status

    def run(self) -> None:
        """
        Start experimental setup, start all devices.
        """

        self._change_status(ExperimentStatus.STARTING)

        try:
            super().start()
        except Exception as e:
            logger.error(str(e), exc_info=e)
            self._change_status(ExperimentStatus.ERROR)
            raise ExperimentError from e
        else:
            self._change_status(ExperimentStatus.RUNNING)

    def finish(self) -> None:
        """
        Stop experimental setup, stop all devices.
        """

        self._change_status(ExperimentStatus.FINISHING)

        try:
            super().stop()
        except Exception as e:
            logger.error(str(e), exc_info=e)
            self._change_status(ExperimentStatus.ERROR)
            raise ExperimentError from e
        else:
            self._change_status(ExperimentStatus.FINISHED)

    def start(self) -> None:
        """
        Alias for ExperimentManager.run()
        """
        self.run()

    def stop(self) -> None:
        """
        Alias for ExperimentManager.finish()
        """
        self.finish()

    @property
    def status(self) -> ExperimentStatus:
        """
        Get experiment status.

        :return: experiment status enum code.
        """

        return self._status

    def is_finished(self) -> bool:
        """
        Returns true, if the status of the experiment manager is `finished`.

        :return: True if finished, false otherwise
        """
        return self.status == ExperimentStatus.FINISHED

    def is_running(self) -> bool:
        """
        Returns true, if the status of the experiment manager is `running`.

        :return: True if running, false otherwise
        """
        return self.status == ExperimentStatus.RUNNING

    def is_error(self) -> bool:
        """
        Returns true, if the status of the experiment manager is `error`.

        :return: True if on error, false otherwise
        """
        return self.status == ExperimentStatus.ERROR

    def add_device(self, name: str, device: Device) -> None:
        """
        Add a new device to the manager. If the experiment is running, automatically
        start the device. If a device with this name already exists, raise an exception.

        :param name: is the name of the device.
        :param device: is the instantiated Device object.
        :raise DeviceExistingException:
        """

        if self.status == ExperimentStatus.ERROR:
            err_msg = "Experiment is on ERROR, cannot add device"
            logger.error(err_msg)
            raise ExperimentError(err_msg)

        super().add_device(name, device)

        # check experiment status and start device if started
        if self.status == ExperimentStatus.RUNNING:
            logger.info(f"Experiment is already RUNNING, start Device {device}")
            try:
                device.start()
            except Exception as e:
                logger.error(str(e), exc_info=e)
                self._change_status(ExperimentStatus.ERROR)
                raise ExperimentError from e
