#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""

"""

import logging
from typing import (
    Optional,
    Union,
)

import libtiepie as ltp
from libtiepie import oscilloscopechannel as ltp_osc_ch

from .base import (
    TiePieError,
    wrap_libtiepie_exception,
)
from .utils import PublicPropertiesReprMixin
from ...utils.enum import NameEnum
from ...utils.typing import Number
from ...utils.validation import (
    validate_bool,
    validate_number,
)

logger = logging.getLogger(__name__)


class TiePieOscilloscopeChannelCoupling(  # type:ignore
    NameEnum, init="value description"
):
    DCV = ltp.CK_DCV, "DC volt"
    ACV = ltp.CK_ACV, "AC volt"
    DCA = ltp.CK_DCA, "DC current"
    ACA = ltp.CK_ACA, "AC current"


class TiePieOscilloscopeRange(NameEnum):
    TWO_HUNDRED_MILLI_VOLT = 0.2
    FOUR_HUNDRED_MILLI_VOLT = 0.4
    EIGHT_HUNDRED_MILLI_VOLT = 0.8
    TWO_VOLT = 2
    FOUR_VOLT = 4
    EIGHT_VOLT = 8
    TWENTY_VOLT = 20
    FORTY_VOLT = 40
    EIGHTY_VOLT = 80

    @staticmethod
    def suitable_range(value):
        try:
            return TiePieOscilloscopeRange(value)
        except ValueError:
            attrs = [ra.value for ra in TiePieOscilloscopeRange]
            chosen_range: Optional[TiePieOscilloscopeRange] = None
            for attr in attrs:
                if value < attr:
                    chosen_range = TiePieOscilloscopeRange(attr)
                    logger.warning(
                        f"Desired value ({value} V) not possible."
                        f"Next larger range ({chosen_range.value} V) "
                        f"selected."
                    )
                    break
            if chosen_range is None:
                chosen_range = TiePieOscilloscopeRange.EIGHTY_VOLT
                logger.warning(
                    f"Desired value ({value} V) is over the maximum; "
                    f"largest range ({chosen_range.value} V) selected"
                )
            return chosen_range


class TiePieOscilloscopeTriggerKind(NameEnum, init="value description"):  # type:ignore
    RISING = ltp.TK_RISINGEDGE, "Rising"
    FALLING = ltp.TK_FALLINGEDGE, "Falling"
    ANY = ltp.TK_ANYEDGE, "Any"
    RISING_OR_FALLING = ltp.TK_ANYEDGE, "Rising or Falling"


class TiePieOscilloscopeTriggerLevelMode(  # type:ignore
    NameEnum, init="value description"
):
    UNKNOWN = ltp.TLM_UNKNOWN, "Unknown"
    RELATIVE = ltp.TLM_RELATIVE, "Relative"
    ABSOLUTE = ltp.TLM_ABSOLUTE, "Absolute"


class SafeGround:
    """
    Class that dynamically adds the safe_ground_enabled attribute getter/setter
    if the bound oscilloscope has the safe ground option.
    """
    def __get__(self, instance, owner):
        if not instance.channel.has_safe_ground:
            msg = "The oscilloscope has no safe ground option."
            logger.error(msg)
            raise TiePieError(msg)

        return instance.channel.safe_ground_enabled

    def __set__(self, instance, value):
        if not instance.channel.has_safe_ground:
            msg = "The oscilloscope has no safe ground option."
            raise TiePieError(msg)
        validate_bool("safe ground enabled", value, logger=logger)
        instance.channel.safe_ground_enabled = value
        if value:
            msg = "enabled"
        else:
            msg = "disabled"
        logger.info(f"Safe ground is set to {msg}.")


class TiePieOscilloscopeChannelConfig(PublicPropertiesReprMixin):
    """
    Oscilloscope's channel configuration, with cleaning of
    values in properties setters as well as setting and reading them on and
    from the device's channel.
    """

    def __init__(self, ch_number: int, channel: ltp_osc_ch.OscilloscopeChannel):
        self.ch_number: int = ch_number
        self.channel: ltp_osc_ch.OscilloscopeChannel = channel
        self.param_lim: TiePieOscilloscopeChannelConfigLimits = (
            TiePieOscilloscopeChannelConfigLimits(osc_channel=channel)
        )

    @staticmethod
    def clean_coupling(
        coupling: Union[str, TiePieOscilloscopeChannelCoupling]
    ) -> TiePieOscilloscopeChannelCoupling:
        return TiePieOscilloscopeChannelCoupling(coupling)

    @property  # type: ignore
    @wrap_libtiepie_exception
    def coupling(self) -> TiePieOscilloscopeChannelCoupling:
        return TiePieOscilloscopeChannelCoupling(self.channel.coupling)

    @coupling.setter
    def coupling(self, coupling: Union[str, TiePieOscilloscopeChannelCoupling]) -> None:
        self.channel.coupling = self.clean_coupling(coupling).value
        logger.info(f"Coupling is set to {coupling}.")

    @staticmethod
    def clean_enabled(enabled: bool) -> bool:
        validate_bool("channel enabled", enabled, logger=logger)
        return enabled

    @property
    def enabled(self) -> bool:
        return self.channel.enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        self.channel.enabled = self.clean_enabled(enabled)
        if enabled:
            msg = "enabled"
        else:
            msg = "disabled"
        logger.info(f"Channel {self.ch_number} is set to {msg}.")

    def clean_input_range(
        self, input_range: Union[float, TiePieOscilloscopeRange]
    ) -> TiePieOscilloscopeRange:
        if not isinstance(input_range, TiePieOscilloscopeRange):
            validate_number(
                "input range",
                input_range,
                self.param_lim.input_range,
                logger=logger,
            )
        return TiePieOscilloscopeRange.suitable_range(input_range)

    @property
    def input_range(self) -> TiePieOscilloscopeRange:
        return TiePieOscilloscopeRange(self.channel.range)

    @input_range.setter
    def input_range(self, input_range: Union[float, TiePieOscilloscopeRange]) -> None:
        input_range = self.clean_input_range(input_range).value
        self.channel.range = input_range
        self.param_lim.trigger_level_abs = (-input_range, input_range)
        logger.info(f"input range is set to {self.channel.range} V.")

    def clean_probe_offset(self, probe_offset: float) -> float:
        validate_number(
            "probe offset", probe_offset, self.param_lim.probe_offset, logger=logger
        )
        return float(probe_offset)

    @property
    def probe_offset(self) -> float:
        return self.channel.probe_offset

    @probe_offset.setter
    def probe_offset(self, probe_offset: float) -> None:
        self.channel.probe_offset = self.clean_probe_offset(probe_offset)
        logger.info(f"Probe offset is set to {probe_offset:_.3f}.")

    @property  # type: ignore
    @wrap_libtiepie_exception
    def has_safe_ground(self) -> bool:
        """
        Check whether bound oscilloscope device has "safe ground" option

        :return: bool: 1=safe ground available
        """
        return self.channel.has_safe_ground

    def clean_trigger_hysteresis(self, trigger_hysteresis: float) -> float:
        validate_number(
            "trigger hysteresis",
            trigger_hysteresis,
            self.param_lim.trigger_hysteresis,
            logger=logger,
        )
        return float(trigger_hysteresis)

    @property
    def trigger_hysteresis(self) -> float:
        return self.channel.trigger.hystereses[0]

    @trigger_hysteresis.setter
    def trigger_hysteresis(self, trigger_hysteresis: float) -> None:
        self.channel.trigger.hystereses[0] = self.clean_trigger_hysteresis(
            trigger_hysteresis
        )
        logger.info(f"Trigger hysteresis is set to {trigger_hysteresis}.")

    @staticmethod
    def clean_trigger_kind(
        trigger_kind: Union[str, TiePieOscilloscopeTriggerKind]
    ) -> TiePieOscilloscopeTriggerKind:
        return TiePieOscilloscopeTriggerKind(trigger_kind)

    @property
    def trigger_kind(self) -> TiePieOscilloscopeTriggerKind:
        return TiePieOscilloscopeTriggerKind(self.channel.trigger.kind)

    @trigger_kind.setter
    def trigger_kind(
        self, trigger_kind: Union[str, TiePieOscilloscopeTriggerKind]
    ) -> None:
        self.channel.trigger.kind = self.clean_trigger_kind(trigger_kind).value
        logger.info(f"Trigger kind is set to {trigger_kind}.")

    @staticmethod
    def clean_trigger_level_mode(
        level_mode: Union[str, TiePieOscilloscopeTriggerLevelMode]
    ) -> TiePieOscilloscopeTriggerLevelMode:
        return TiePieOscilloscopeTriggerLevelMode(level_mode)

    @property
    def trigger_level_mode(self) -> TiePieOscilloscopeTriggerLevelMode:
        return TiePieOscilloscopeTriggerLevelMode(self.channel.trigger.level_mode)

    @trigger_level_mode.setter
    def trigger_level_mode(
        self, level_mode: Union[str, TiePieOscilloscopeTriggerLevelMode]
    ) -> None:
        level_mode_ = self.clean_trigger_level_mode(level_mode)
        self.channel.trigger.level_mode = level_mode_.value
        logger.info(f"Trigger level mode is set to {level_mode_.name}.")

    def clean_trigger_level(self, trigger_level: Number) -> float:
        if self.trigger_level_mode == TiePieOscilloscopeTriggerLevelMode.RELATIVE:
            validate_number(
                "trigger level",
                trigger_level,
                self.param_lim.trigger_level_rel,
                float,
                logger=logger,
            )
        if self.trigger_level_mode == TiePieOscilloscopeTriggerLevelMode.ABSOLUTE:
            validate_number(
                "trigger level",
                trigger_level,
                self.param_lim.trigger_level_abs,
                (int, float),
                logger=logger,
            )
        return float(trigger_level)

    @property
    def trigger_level(self) -> float:
        return self.channel.trigger.levels[0]

    @trigger_level.setter
    def trigger_level(self, trigger_level: Number) -> None:
        self.channel.trigger.levels[0] = self.clean_trigger_level(trigger_level)
        if self.trigger_level_mode == TiePieOscilloscopeTriggerLevelMode.RELATIVE:
            logger.info(f"Trigger level is set to {trigger_level}.")
        if self.trigger_level_mode == TiePieOscilloscopeTriggerLevelMode.ABSOLUTE:
            logger.info(f"Trigger level is set to {trigger_level} V.")

    @staticmethod
    def clean_trigger_enabled(trigger_enabled):
        validate_bool("Trigger enabled", trigger_enabled, logger=logger)
        return trigger_enabled

    @property
    def trigger_enabled(self) -> bool:
        return self.channel.trigger.enabled

    @trigger_enabled.setter
    def trigger_enabled(self, trigger_enabled: bool) -> None:
        self.channel.trigger.enabled = self.clean_trigger_enabled(trigger_enabled)
        if trigger_enabled:
            msg = "enabled"
        else:
            msg = "disabled"
        logger.info(f"Trigger is set to {msg}.")


class TiePieOscilloscopeChannelConfigLimits:
    """
    Default limits for oscilloscope channel parameters.
    """

    def __init__(self, osc_channel: ltp_osc_ch.OscilloscopeChannel) -> None:
        self.input_range = (osc_channel.ranges[0], osc_channel.ranges[-1])  # [V]
        self.probe_offset = (-1e6, 1e6)  # [V], [A] or [Ohm]
        self.trigger_hysteresis = (0, 1)
        self.trigger_level_rel = (0, 1)
        self.trigger_level_abs = (-osc_channel.ranges[-1], osc_channel.ranges[-1])
