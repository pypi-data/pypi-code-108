from ingenialink.utils._utils import raise_err
from ingenialink.poller import Poller
from .constants import *

from datetime import datetime
from threading import Timer, RLock

import ingenialogger
logger = ingenialogger.get_logger(__name__)


class PollerTimer:
    """Custom timer for the CanopenPoller.

    Args:
        time (int): Timeout to use for the timer.
        cb (function): Callback.

    """
    def __init__(self, time, cb):
        self.cb = cb
        self.time = time
        self.thread = Timer(self.time, self.handle_function)

    def handle_function(self):
        """Handle method that creates the timer for the poller"""
        self.cb()
        self.thread = Timer(self.time, self.handle_function)
        self.thread.start()

    def start(self):
        """Starts the poller timer"""
        self.thread.start()

    def cancel(self):
        """Stops the poller timer"""
        self.thread.cancel()
        if self.thread.is_alive():
            self.thread.join()


class CanopenPoller(Poller):
    """Register poller for CANOpen communications.

    Args:
        servo (CanopenServo): Servo.
        num_channels (int): Number of channels.

    Raises:
        ILCreationError: If the poller could not be created.

    """

    def __init__(self, servo, num_channels):
        super(CanopenPoller, self).__init__(servo, num_channels)
        self.__sz = 0
        self.__refresh_time = 0
        self.__time_start = 0.0
        self.__samples_count = 0
        self.__samples_lost = False
        self.__timer = None
        self.__running = False
        self.__mappings = []
        self.__mappings_enabled = []
        self.__lock = RLock()
        self._reset_acq()

    def start(self):
        """Start the poller."""

        if self.__running:
            logger.warning("Poller already running")
            raise_err(IL_EALREADY)

        # Activate timer
        self.__timer = PollerTimer(self.__refresh_time,
                                   self._acquire_callback_poller_data)
        self.__timer.start()
        self.__time_start = datetime.now()

        self.__running = True

        return 0

    def stop(self):
        """Stop poller."""

        if self.__running:
            self.__timer.cancel()

        self.__running = False

    def configure(self, t_s, sz):
        """Configure data.

        Args:
            t_s (int, float): Polling period (s).
            sz (int): Buffer size.

        Returns:
            int: Status code.

        Raises:
            ILStateError: The poller is already running.

        """
        if self.__running:
            logger.warning("Poller is running")
            raise_err(IL_ESTATE)

        # Configure data and sizes with empty data
        self._reset_acq()
        self.__sz = sz
        self.__refresh_time = t_s
        self.__acq['t'] = [0] * sz
        for channel in range(0, self.num_channels):
            data_channel = [0] * sz
            self.__acq['d'].append(data_channel)
            self.__mappings.append('')
            self.__mappings_enabled.append(False)

        return 0

    def ch_configure(self, channel, reg):
        """Configure a poller channel mapping.

        Args:
            channel (int): Channel to be configured.
            reg (Register): Register to associate to the given channel.

        Returns:
            int: Status code.

        Raises:
            ILStateError: The poller is already running.
            ILValueError: Channel out of range.
            TypeError: If the register is not valid.

        """

        if self.__running:
            logger.warning("Poller is running")
            raise_err(IL_ESTATE)

        if channel > self.num_channels:
            logger.error("Channel out of range")
            raise_err(IL_EINVAL)

        # Obtain register
        _reg = self.servo._get_reg(reg)

        # Reg identifier obtained and set enabled
        self.__mappings[channel] = {}
        self.__mappings[channel][_reg.identifier] = int(_reg.subnode)
        self.__mappings_enabled[channel] = True

        return 0

    def ch_disable(self, channel):
        """Disable a channel.

        Args:
            channel (int): Channel to be disabled.

        Raises:
            ILStateError: The poller is already running.
            ILValueError: Channel out of range.

        Returns:
            int: Status code.

        """

        if self.__running:
            logger.warning("Poller is running")
            raise_err(IL_ESTATE)

        if channel > self.num_channels:
            logger.error("Channel out of range")
            raise_err(IL_EINVAL)

        # Set channel required as disabled
        self.__mappings_enabled[channel] = False

        return 0

    def ch_disable_all(self):
        """Disable all channels.

        Returns:
            int: Status code.

        """
        for channel in range(self.num_channels):
            r = self.ch_disable(channel)
            if r < 0:
                raise_err(r)
        return 0

    def _reset_acq(self):
        """Resets the acquired channels."""
        self.__acq = {
            "t": [],
            "d": []
        }

    def _acquire_callback_poller_data(self):
        """Acquire callback for poller data."""
        time_diff = datetime.now()
        delta = time_diff - self.__time_start

        # Obtain current time
        t = delta.total_seconds()

        self.__lock.acquire()
        # Acquire all configured channels
        if self.__samples_count >= self.__sz:
            self.__samples_lost = True
        else:
            self.__acq['t'][self.__samples_count] = t

            # Acquire enabled channels, comprehension list indexes obtained
            enabled_channel_indexes = [
                channel_idx for channel_idx, is_enabled in
                enumerate(self.__mappings_enabled) if is_enabled
            ]

            for channel in enabled_channel_indexes:
                for register_identifier, subnode in \
                        self.__mappings[channel].items():
                    self.__acq['d'][channel][self.__samples_count] = \
                        self.servo.read(register_identifier, subnode)

            # Increment samples count
            self.__samples_count += 1

        self.__lock.release()

    @property
    def data(self):
        """tuple (list, list, bool): Time vector, array of data vectors and a
            flag indicating if data was lost."""
        t = list(self.__acq['t'][0:self.__samples_count])
        d = []

        # Acquire enabled channels, comprehension list indexes obtained
        enabled_channel_indexes = [
            channel_idx for channel_idx, is_enabled in
            enumerate(self.__mappings_enabled) if is_enabled
        ]

        for channel in range(self.num_channels):
            if self.__mappings_enabled[channel]:
                d.append(
                    list(self.__acq['d'][channel][0:self.__samples_count])
                )
            else:
                d.append(list(None))

        self.__lock.acquire()
        self.__samples_count = 0
        self.__samples_lost = False
        self.__lock.release()

        return t, d, self.__samples_lost
