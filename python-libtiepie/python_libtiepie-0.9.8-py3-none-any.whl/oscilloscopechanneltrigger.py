from .api import api
from .const import *
from .library import library
from .oscilloscopechanneltriggerlevels import OscilloscopeChannelTriggerLevels
from .oscilloscopechanneltriggerhystereses import OscilloscopeChannelTriggerHystereses
from .oscilloscopechanneltriggertimes import OscilloscopeChannelTriggerTimes


class OscilloscopeChannelTrigger(object):
    """"""

    def __init__(self, handle, ch):
        self._handle = handle
        self._ch = ch
        self._levels = OscilloscopeChannelTriggerLevels(handle, ch)
        self._hystereses = OscilloscopeChannelTriggerHystereses(handle, ch)
        self._times = OscilloscopeChannelTriggerTimes(handle, ch)

    def _get_levels(self):
        return self._levels

    def _get_hystereses(self):
        return self._hystereses

    def _get_times(self):
        return self._times

    def _get_is_available(self):
        """ Check whether the channel trigger is available, with the current oscilloscope settings. """
        value = api.ScpChTrIsAvailable(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_triggered(self):
        """ Check whether the channel trigger caused a trigger. """
        value = api.ScpChTrIsTriggered(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_enabled(self):
        """ Check whether channel trigger is enabled. """
        value = api.ScpChTrGetEnabled(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_enabled(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.ScpChTrSetEnabled(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_kinds(self):
        """ Supported channel trigger kinds with the currently selected measure mode. """
        value = api.ScpChTrGetKinds(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_kind(self):
        """ Currently selected channel trigger kind. """
        value = api.ScpChTrGetKind(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_kind(self, value):
        api.ScpChTrSetKind(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_level_modes(self):
        """ Supported trigger level modes. """
        value = api.ScpChTrGetLevelModes(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_level_mode(self):
        """ Current trigger level mode. """
        value = api.ScpChTrGetLevelMode(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_level_mode(self, value):
        api.ScpChTrSetLevelMode(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    def _get_conditions(self):
        """ Supported trigger conditions with the currently selected trigger kind. """
        value = api.ScpChTrGetConditions(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _get_condition(self):
        """ Current selected trigger condition. """
        value = api.ScpChTrGetCondition(self._handle, self._ch)
        library.check_last_status_raise_on_error()
        return value

    def _set_condition(self, value):
        api.ScpChTrSetCondition(self._handle, self._ch, value)
        library.check_last_status_raise_on_error()

    is_available = property(_get_is_available)
    is_triggered = property(_get_is_triggered)
    enabled = property(_get_enabled, _set_enabled)
    kinds = property(_get_kinds)
    kind = property(_get_kind, _set_kind)
    level_modes = property(_get_level_modes)
    level_mode = property(_get_level_mode, _set_level_mode)
    conditions = property(_get_conditions)
    condition = property(_get_condition, _set_condition)
    levels = property(_get_levels)
    hystereses = property(_get_hystereses)
    times = property(_get_times)
