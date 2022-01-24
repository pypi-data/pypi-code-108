#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock OscilloscopeChannelTrigger
"""

import libtiepie.const as const
from libtiepie.oscilloscopechanneltrigger import (
    OscilloscopeChannelTrigger as LtpOscilloscopeChannelTrigger,
)

from .oscilloscopechanneltriggerhystereses import OscilloscopeChannelTriggerHystereses
from .oscilloscopechanneltriggerlevels import OscilloscopeChannelTriggerLevels


class OscilloscopeChannelTrigger(LtpOscilloscopeChannelTrigger):
    def __init__(self):
        self._enabled = False
        self._hystereses = OscilloscopeChannelTriggerHystereses()
        self._levels = OscilloscopeChannelTriggerLevels()
        self._kind = const.TK_ANYEDGE
        self._level_mode = const.TLM_UNKNOWN

    def _get_enabled(self):
        return self._enabled

    def _set_enabled(self, value):
        self._enabled = value

    def _get_hystereses(self):
        return self._hystereses

    def _get_levels(self):
        return self._levels

    def _get_kind(self):
        return self._kind

    def _set_kind(self, value):
        self._kind = value

    def _get_level_mode(self):
        return self._level_mode

    def _set_level_mode(self, value):
        self._level_mode = value

    enabled = property(_get_enabled, _set_enabled)
    hystereses = property(_get_hystereses)
    levels = property(_get_levels)
    kind = property(_get_kind, _set_kind)
    level_mode = property(_get_level_mode, _set_level_mode)
