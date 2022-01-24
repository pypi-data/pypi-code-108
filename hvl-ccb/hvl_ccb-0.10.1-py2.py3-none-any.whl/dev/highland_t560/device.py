#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Module for controlling device, including TRIG, CLOCK and GATE I/Os.
"""
import logging
import re
from typing import Union

from hvl_ccb.configuration import configdataclass
from hvl_ccb.dev import SingleCommDevice
from hvl_ccb.dev.highland_t560.base import (
    T560Communication,
    T560Error,
    AutoInstallMode,
    TriggerMode,
    _TriggerStatus,
    GateMode,
    _GateStatus,
    Polarity,
)
from hvl_ccb.dev.highland_t560.channel import _Channel
from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_number

logger = logging.getLogger(__name__)


@configdataclass
class T560Config:
    auto_install_mode = AutoInstallMode.INSTALL


class T560(SingleCommDevice):
    def __init__(self, com, dev_config=None):
        super().__init__(com, dev_config)
        logger.info("Highland T560 DDG initialized.")
        # Channel interfaces
        self._ch_a = _Channel(self, "A")
        self._ch_b = _Channel(self, "B")
        self._ch_c = _Channel(self, "C")
        self._ch_d = _Channel(self, "D")
        self.channels = (self.ch_a, self.ch_b, self.ch_c, self.ch_d)
        self.auto_install_mode = self.config.auto_install_mode

        # Disable all channels by default
        for channel in self.channels:
            channel.enabled = False
            logger.info(f"{channel.ch_name} initialized")

    @staticmethod
    def config_cls():
        return T560Config

    @staticmethod
    def default_com_cls():
        return T560Communication

    @property
    def ch_a(self) -> _Channel:
        """
        Channel A of T560
        """
        return self._ch_a

    @property
    def ch_b(self) -> _Channel:
        """
        Channel B of T560
        """
        return self._ch_b

    @property
    def ch_c(self) -> _Channel:
        """
        Channel C of T560
        """
        return self._ch_c

    @property
    def ch_d(self) -> _Channel:
        """
        Channel D of T560
        """
        return self._ch_d

    @property
    def _status(self) -> str:
        """
        Log and return device status as a string
        """
        status_str = self.com.query("STATUS")
        logger.info(f"T560 status: {status_str}")
        return status_str

    def save_device_configuration(self):
        """
        Save the current settings to nonvolatile memory.
        """
        self.com.query("SA")
        logger.info("Current device settings saved")

    def load_device_configuration(self):
        """
        Load the settings saved in nonvolatile memory.
        """
        self.com.query("RE")
        logger.info("Stored device settings loaded")

    @property
    def auto_install_mode(self) -> AutoInstallMode:
        """
        Check the autoinstall settings of the T560.
        The autoinstall mode sets how changes to device settings are applied.
        See manual section 4.7.2 for more information about these modes.
        """
        mode = AutoInstallMode(int(self.com.query("AU")))
        logger.info(f"auto-install mode: {mode.name}")
        return mode

    @auto_install_mode.setter
    def auto_install_mode(self, mode: Union[int, AutoInstallMode]):
        """
        Change the autoinstall settings of the T560.
        If mode is 0, turn OFF autoinstall.
        If mode is 1, use INSTALL (normal) mode.
        If mode is 2, use QUEUE mode.
        """
        mode = AutoInstallMode(mode)
        self.com.query(f"AU {mode}")
        logger.info(f"auto-install mode set to {mode.name}")

    def activate_clock_output(self):
        """
        Outputs 10 MHz clock signal
        """
        self.com.query("CL OU")
        logger.info("Clock output activated")

    def use_external_clock(self):
        """
        Finds and accepts an external clock signal to the CLOCK input
        """
        self.com.query("CL IN")
        logger.info("Clock input accepted")

    @property
    def _trigger_status(self) -> _TriggerStatus:
        """
        Get the device trigger settings from the T560.

        Example response:
        "Trig REM HIZ Level 1.250 Div 0000000000 SYN 00010000.00"
        """
        response = self.com.query("TR")
        pattern_mode = r"Trig\s*(?P<mode>\w+)"
        pattern_termination = r"(?P<termination>\w+)"
        pattern_level = r"Level\s*(?P<level>[0-9,._]+)"
        pattern_divisor = r"Div\s*(?P<divisor>[0-9,._]+)"
        pattern_frequency = r"SYN\s*(?P<frequency>[0-9,._]+)"
        # Check for valid response with regex
        pattern = (
            rf"{pattern_mode}\s*{pattern_termination}\s*"
            rf"{pattern_level}\s*{pattern_divisor}\s*{pattern_frequency}"
        )
        result = re.search(pattern, response)
        if not result:
            msg = f"Cannot identify the trigger status. Got: '{response}'"
            logger.error(msg)
            raise T560Error(msg)

        mode = TriggerMode(result.group("mode"))
        level = float(result.group("level").replace(",", "_"))
        frequency = float(result.group("frequency").replace(",", "_"))
        return _TriggerStatus(mode=mode, level=level, frequency=frequency)

    @property
    def trigger_mode(self):
        """
        Get device trigger source.
        """
        mode = self._trigger_status.mode
        logger.info(f"Trigger mode: {mode}")
        return mode

    @trigger_mode.setter
    def trigger_mode(self, mode: Union[str, TriggerMode]):
        """
        Select device trigger source.
        Arms device by enabling triggers for selected source.

        :param mode: Available trigger modes, see TriggerMode enum
        """
        self.com.query(f"TR {TriggerMode(mode)}")
        logger.info(f"Trigger mode set to {mode}")

    @property
    def trigger_level(self):
        """
        Get external trigger level.
        """
        level = self._trigger_status.level
        logger.info(f"Trigger level: {level} V")
        return level

    @trigger_level.setter
    def trigger_level(self, level: Number):
        """
        Set external trigger level.

        :param level:  EXT trigger level in volts
        :raises ValueError: if outside +0.25 to 3.3V limits
        """
        validate_number("trigger level", level, limits=(0.25, 3.3), logger=logger)
        self.com.query(f"TL {level}")
        logger.info(f"Trigger level set to {level} V")

    @property
    def frequency(self) -> float:
        """
        The frequency of the timing cycle in Hz.
        """

        frequency = self._trigger_status.frequency
        logger.info(f"Device synthesizer frequency: {frequency} Hz")
        return frequency

    @frequency.setter
    def frequency(self, frequency: Number):
        """
        Setter method for the crystal oscillator frequency.

        :param frequency: frequency in Hz, resolution .018 Hz.
        :raises ValueError: if less than .018 Hz, or greater than 16 MHz.
        """
        validate_number(
            "frequency", frequency, limits=(0.018, 16_000_000), logger=logger
        )
        self.com.query(f"SY {frequency:.3f}")
        logger.info(f"Device synthesizer frequency set to {frequency} Hz")

    @property
    def period(self) -> float:
        """
        The period of the timing cycle (time between triggers) in seconds.
        """
        return 1 / self._trigger_status.frequency

    @period.setter
    def period(self, period: Number):
        """
        Setter method for the period property.

        :param period: Period in seconds.
        :raises ValueError: if less than 62.5 ns or greater than 10 s
        """
        validate_number("period", period, (62.5e-9, 10), logger=logger)
        self.frequency = 1 / period

    def fire_trigger(self):
        """
        Fire a software trigger.
        """
        self.com.query("FI")
        logger.info("Remote trigger sent")

    def disarm_trigger(self):
        """
        Disarm DDG by disabling all trigger sources.
        """
        self.trigger_mode = TriggerMode.OFF
        logger.info("Trigger sources disabled")

    @property
    def _gate_status(self) -> _GateStatus:
        """
        Get the settings from the GATE I/O port of the T560.
        GATE may be used as an input to enable/disable TRIG output,
        or as an output to monitor when TRIG is enabled.

        Example response:
        "Gate OFF POS HIZ Shots 0000000066"
        """
        response = self.com.query("GA")
        pattern_mode = r"Gate\s*(?P<mode>\w+)"
        pattern_polarity = r"(?P<polarity>\w+)"
        pattern_termination = r"(?P<termination>\w+)"
        pattern_counter = r"Shots\s*(?P<counter>[0-9,.]+)"
        # Check for valid response with regex
        pattern = (
            rf"{pattern_mode}\s*{pattern_polarity}\s*"
            rf"{pattern_termination}\s*{pattern_counter}"
        )
        result = re.search(pattern, response)
        if not result:
            msg = f"Cannot identify the gate status. Got: '{response}'"
            logger.error(msg)
            raise T560Error(msg)

        mode = GateMode(result.group("mode"))
        polarity = Polarity(result.group("polarity"))
        return _GateStatus(mode=mode, polarity=polarity)

    @property
    def gate_mode(self) -> GateMode:
        """
        Check the mode setting of the GATE I/O port.
        """
        mode = self._gate_status.mode
        logger.info(f"Gate mode: {mode}")
        return mode

    @gate_mode.setter
    def gate_mode(self, mode: Union[str, GateMode]):
        """
        Choose to disable GATE, or use as an input or output

        :param mode: "OFF", "IN", or "OUT". See GateMode enum.
        :raises ValueError: if mode is not in GateMode enum
        """
        self.com.query(f"GA {GateMode(mode)}")
        logger.info(f"Gate mode set to {mode}")

    @property
    def gate_polarity(self) -> Polarity:
        """
        Check the polarity setting of the GATE I/O port.
        """
        polarity = self._gate_status.polarity
        logger.info(f"Gate polarity: {polarity}")
        return polarity

    @gate_polarity.setter
    def gate_polarity(self, polarity: Union[str, Polarity]):
        """
        Set the polarity of the GATE I/O port.

        :param polarity: "POS" or "NEG", see Polarity enum
        :raises ValueError: if polarity is not in Polarity enum
        """
        self.com.query(f"GA {Polarity(polarity)}")
        logger.info(f"Gate polarity set to {polarity}")
