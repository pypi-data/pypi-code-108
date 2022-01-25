from ctypes import *
from .api import api
from .const import *
from .library import library


class TriggerOutput(object):
    """"""

    def __init__(self, handle, index):
        self._handle = handle
        self._index = index

    def _get_enabled(self):
        """ Check whether a trigger output is enabled. """
        value = api.DevTrOutGetEnabled(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_enabled(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.DevTrOutSetEnabled(self._handle, self._index, value)
        library.check_last_status_raise_on_error()

    def _get_events(self):
        """ Supported trigger output events. """
        value = api.DevTrOutGetEvents(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value

    def _get_event(self):
        """ Currently selected trigger output event. """
        value = api.DevTrOutGetEvent(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value

    def _set_event(self, value):
        api.DevTrOutSetEvent(self._handle, self._index, value)
        library.check_last_status_raise_on_error()

    def _get_id(self):
        """ Id. """
        value = api.DevTrOutGetId(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return value

    def _get_name(self):
        """ Name. """
        length = api.DevTrOutGetName(self._handle, self._index, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.DevTrOutGetName(self._handle, self._index, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def trigger(self):
        """ Trigger the specified device trigger output.

        :returns: ``True`` if successful, ``False`` otherwise.
        .. versionadded:: 0.6
        """
        result = api.DevTrOutTrigger(self._handle, self._index)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    enabled = property(_get_enabled, _set_enabled)
    events = property(_get_events)
    event = property(_get_event, _set_event)
    id = property(_get_id)
    name = property(_get_name)
