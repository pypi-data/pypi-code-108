from ctypes import *
from .api import api
from .const import *
from .library import library


class TriggerInput(object):
    """"""

    def __init__(self, handle, index):
        self._handle = handle
        self._index = index

    def _get_is_triggered(self):
        """ Check whether the trigger input caused a trigger. """
        value = api.ScpTrInIsTriggered(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_enabled(self):
        """ Check whether a device trigger input is enabled. """
        value = api.DevTrInGetEnabled(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_enabled(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.DevTrInSetEnabled(self._handle, self._index, value)
        library.check_last_status_raise_on_error()

    def _get_kinds(self):
        """ Supported trigger kinds. """
        value = api.DevTrInGetKinds(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value

    def _get_kind(self):
        """ Currently selected trigger kind. """
        value = api.DevTrInGetKind(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value

    def _set_kind(self, value):
        api.DevTrInSetKind(self._handle, self._index, value)
        library.check_last_status_raise_on_error()

    def _get_is_available(self):
        """ Check whether a device trigger input is available. """
        value = api.DevTrInIsAvailable(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_id(self):
        """ Id. """
        value = api.DevTrInGetId(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value

    def _get_name(self):
        """ Name. """
        length = api.DevTrInGetName(self._handle, self._index, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.DevTrInGetName(self._handle, self._index, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    is_triggered = property(_get_is_triggered)
    enabled = property(_get_enabled, _set_enabled)
    kinds = property(_get_kinds)
    kind = property(_get_kind, _set_kind)
    is_available = property(_get_is_available)
    id = property(_get_id)
    name = property(_get_name)
