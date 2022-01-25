from .api import api
from .const import *
from .library import library


class Object(object):
    """"""

    def __init__(self, handle):
        self._handle = handle

    def __del__(self):
        api.ObjClose(self._handle)

    def _get_is_removed(self):
        """ Check whether an object is removed. """
        value = api.ObjIsRemoved(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_interfaces(self):
        """ Check which interface are supported by the specified object. """
        value = api.ObjGetInterfaces(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def set_event_callback(self, callback, data):
        """ Set a callback function which is called when an event occurs.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        .. versionadded:: 0.6
        """
        api.ObjSetEventCallback(self._handle, callback, data)
        library.check_last_status_raise_on_error()

    def get_event(self, event, value):
        """ Get an event form the event queue.

        :param event: Pointer to store the event.
        :param value: Pointer to store the event value or ``None.``
        :returns: ``True`` if an event is available, ``False`` otherwise.
        .. versionadded:: 0.6
        """
        result = api.ObjGetEvent(self._handle, event, value)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    if platform.system() == 'Linux':
        def set_event_event(self, event):
            """ Set an event file descriptor which is set when an event occurs.

            :param event: An event file descriptor. Use <tt><0</tt> to disable.
            .. versionadded:: 0.6
            """
            api.ObjSetEventEvent(self._handle, event)
            library.check_last_status_raise_on_error()

    if platform.system() == 'Windows':
        def set_event_event(self, event):
            """ Set an event object handle which is set when an event occurs.

            :param event: A handle to the event object. Use ``None`` to disable.
            .. versionadded:: 0.6
            """
            api.ObjSetEventEvent(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_event_window_handle(self, wnd):
            """ Set a window handle to which a #WM_LIBTIEPIE_EVENT message is sent when an event occurs.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            .. versionadded:: 0.6
            """
            api.ObjSetEventWindowHandle(self._handle, wnd)
            library.check_last_status_raise_on_error()

    is_removed = property(_get_is_removed)
    interfaces = property(_get_interfaces)
