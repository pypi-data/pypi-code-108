#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Module for controlling pulse output channels A, B, C and D.
"""
import logging
import re
from typing import Union

from hvl_ccb.dev.highland_t560.base import T560Error, Polarity, _ChannelStatus
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_bool, validate_number

logger = logging.getLogger(__name__)


class _Channel:
    """
    A T560 channel
    """

    def __init__(self, device, name):
        self.ch_name = name
        self.device = device  # The T560 object

    @property
    def _status(self) -> _ChannelStatus:
        """
        Get the settings of the channel from the T560. Example response:
        "Ch A  POS  ON  Dly  00.000,000,000,000  Wid  00.000,002,000,000"
        """
        response = self.device.com.query(f"{self.ch_name}S")
        # Check for valid response with regex
        pattern_name = rf"Ch\s*{self.ch_name}"
        pattern_polarity = r"(?P<polarity>\w+)"
        pattern_enabled = r"(?P<enabled>\w+)"
        pattern_delay = r"Dly\s*(?P<delay>[0-9,.]+)"
        pattern_width = r"Wid\s*(?P<width>[0-9,.]+)"
        pattern = (
            rf"{pattern_name}\s*{pattern_polarity}\s*{pattern_enabled}\s*"
            rf"{pattern_delay}\s*{pattern_width}"
        )
        result = re.search(pattern, response)
        if not result:
            msg = f"Cannot identify the channel status. Got: '{response}'"
            logger.error(msg)
            raise T560Error(msg)

        polarity = Polarity(result.group("polarity"))
        enabled = result.group("enabled") == "ON"
        delay = float(result.group("delay").replace(",", "_"))
        width = float(result.group("width").replace(",", "_"))
        return _ChannelStatus(
            polarity=polarity, enabled=enabled, delay=delay, width=width
        )

    @property
    def enabled(self) -> bool:
        """
        Channel output ON/OFF
        """
        enabled = self._status.enabled
        if enabled:
            logger.info(f"Ch {self.ch_name} is enabled")
        else:
            logger.info(f"Ch {self.ch_name} is disabled")
        return enabled

    @enabled.setter
    def enabled(self, enabled: bool):
        """
        Enable or disable the channel.

        :param enabled: channel ON/OFF status as a bool
        :raises TypeError: if enabled is not a bool-like
        """
        validate_bool("enabled", enabled, logger=logger)
        if enabled:
            self.device.com.query(f"{self.ch_name}S ON")
            logger.info(f"Ch {self.ch_name} has been enabled")
        else:
            self.device.com.query(f"{self.ch_name}S OFF")
            logger.info(f"Ch {self.ch_name} has been disabled")

    @property
    def polarity(self) -> Polarity:
        """
        "POS"": the channel is active-high
        "NEG": the channel is active-low
        """
        polarity = self._status.polarity
        logger.info(f"Ch {self.ch_name} polarity: {polarity}")
        return polarity

    @polarity.setter
    def polarity(self, polarity: Union[str, Polarity]):
        """
        Set the polarity of the channel.

        :param polarity: "POS" or "NEG", see Polarity enum
        :raises ValueError: if polarity is not in Polarity enum
        """
        self.device.com.query(f"{self.ch_name}S {Polarity(polarity)}")
        logger.info(f"Ch {self.ch_name} polarity set to {polarity}")

    @property
    def delay(self) -> Number:
        """
        The time between the trigger and the leading edge of the pulse.
        """
        delay = self._status.delay
        logger.info(f"Ch {self.ch_name} pulse width: {delay} s")
        return delay

    @delay.setter
    def delay(self, delay: Number):
        """
        Set the time between the trigger and the leading edge of the pulse.

        :param delay: pulse delay in seconds, 10 ps resolution.
        :raises ValueError: if delay is negative or greater than 10s
        """
        validate_number("delay", delay, limits=(0, 10), logger=logger)
        self.device.com.query(f"{self.ch_name}D {delay:.12f}s")
        logger.info(f"Ch {self.ch_name} pulse width set to {delay} s")

    @property
    def width(self) -> Number:
        """
        Duration of a pulse.
        """
        width = self._status.width
        logger.info(f"Ch {self.ch_name} pulse width: {width} s")
        return width

    @width.setter
    def width(self, width: Number):
        """
        Set the duration of a pulse.

        :param width: pulse width in seconds, 10 ps resolution.
        :raises ValueError: if width is negative or greater than 10s
        """
        validate_number("width", width, limits=(0, 10), logger=logger)
        self.device.com.query(f"{self.ch_name}W {width:.12f}s")
        logger.info(f"Ch {self.ch_name} pulse width set to {width} s")
