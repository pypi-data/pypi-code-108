#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Mock OscilloscopeChannel
"""

import array
import libtiepie.const as const
from libtiepie.oscilloscopechannel import OscilloscopeChannel as LtpOscilloscopeChannel

from .oscilloscopechanneltrigger import OscilloscopeChannelTrigger


class OscilloscopeChannel(LtpOscilloscopeChannel):
    def __init__(self):
        self._safe_ground_enabled = False
        self._enabled = False
        self._trigger = OscilloscopeChannelTrigger()
        self._has_safe_ground = 1

        self._coupling = const.CK_DCV
        self._range = 20
        self._ranges = array.array('f', [0.20, 80.0])
        self._probe_offset = None

    def _get_trigger(self):
        return self._trigger

    def _get_safe_ground_enabled(self):
        return self._safe_ground_enabled

    def _set_safe_ground_enabled(self, value):
        self._safe_ground_enabled = value

    def _get_enabled(self):
        return self._enabled

    def _set_enabled(self, value):
        self._enabled = value

    def _get_range(self):
        return self._range

    def _set_range(self, value):
        self._range = value

    def _get_coupling(self):
        return self._coupling

    def _set_coupling(self, value):
        self._coupling = value

    def _get_probe_offset(self):
        return self._probe_offset

    def _set_probe_offset(self, value):
        self._probe_offset = value

    def _get_has_safe_ground(self):
        return self._has_safe_ground

    def disable_safe_ground_option(self):
        self._has_safe_ground = 0

    def enable_safe_ground_option(self):
        self._has_safe_ground = 1

    def _get_ranges(self):
        return self._ranges

    safe_ground_enabled = property(_get_safe_ground_enabled, _set_safe_ground_enabled)
    enabled = property(_get_enabled, _set_enabled)
    coupling = property(_get_coupling, _set_coupling)
    range = property(_get_range, _set_range)
    trigger = property(_get_trigger)
    probe_offset = property(_get_probe_offset, _set_probe_offset)
    has_safe_ground = property(_get_has_safe_ground)
    ranges = property(_get_ranges)
