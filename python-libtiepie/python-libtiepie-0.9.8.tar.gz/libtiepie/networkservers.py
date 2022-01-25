from ctypes import *
from .api import api
from .const import *
from .library import library
from .exceptions import InvalidIndexError
from .server import Server


class NetworkServers(object):
    """"""

    def __getitem__(self, index):
        try:
            return self.get_by_index(index)
        except (InvalidIndexError):
            raise IndexError()

    def __len__(self):
        return self.count

    def add(self, url):
        """ Add a server to the list of servers.

        :param url: XXX
        :returns: Instance of :class:`.Server`
        .. versionadded:: 0.9
        """
        url = url.encode('utf-8')
        handle = c_uint32(0)
        result = api.NetSrvAdd(url, STRING_LENGTH_NULL_TERMINATED, byref(handle))
        library.check_last_status_raise_on_error()
        return Server(handle.value) if result else None

    def remove(self, url, force):
        """ Remove a server from the list of servers

        :param url: Pointer to URL character buffer.
        :param force: If ``True`` all open devices are closed, if ``False`` remove only succeeds if no devices are open.
        :returns: ``True`` if removed successfully, ``False`` otherwise.
        .. versionadded:: 0.9
        """
        url = url.encode('utf-8')
        force = BOOL8_TRUE if force else BOOL8_FALSE
        result = api.NetSrvRemove(url, STRING_LENGTH_NULL_TERMINATED, force)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def _get_count(self):
        """ Number of servers available. """
        value = api.NetSrvGetCount()
        library.check_last_status_raise_on_error()
        return value

    def get_by_index(self, index):
        """ Get the handle of a server, based on its index in the list of servers

        :param index: A server index, ``0`` .. NetSrvGetCount() - 1.
        :returns: Instance of :class:`.Server`.
        .. versionadded:: 0.9
        """
        result = api.NetSrvGetByIndex(index)
        library.check_last_status_raise_on_error()
        return Server(result)

    def get_by_url(self, url):
        """ Get the handle of a server, based on its URL

        :param url: Pointer to URL character buffer.
        :returns: Instance of :class:`.Server`.
        .. versionadded:: 0.9
        """
        url = url.encode('utf-8')
        result = api.NetSrvGetByURL(url, STRING_LENGTH_NULL_TERMINATED)
        library.check_last_status_raise_on_error()
        return Server(result)

    def set_callback_added(self, callback, data):
        """ Set a callback function which is called when a server is added to the server list.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        .. versionadded:: 0.9
        """
        api.NetSrvSetCallbackAdded(callback, data)
        library.check_last_status_raise_on_error()

    if platform.system() == 'Linux':
        def set_event_added(self, event):
            """ Set an event file descriptor which is set when a server is added to the server list.

            :param event: An event file descriptor. Use ``<0`` to disable.
            .. versionadded:: 0.9
            """
            api.NetSrvSetEventAdded(event)
            library.check_last_status_raise_on_error()

    if platform.system() == 'Windows':
        def set_event_added(self, event):
            """ Set an event object handle which is set when a server is added to the server list.

            :param event: A handle to the event object. Use ``None`` to disable.
            .. versionadded:: 0.9
            """
            api.NetSrvSetEventAdded(event)
            library.check_last_status_raise_on_error()

        def set_message_added(self, wnd):
            """ Set a window handle to which a #WM_LIBTIEPIE_NETSRV_ADDED message is sent when a server is added to the server list.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            .. versionadded:: 0.9
            """
            api.NetSrvSetMessageAdded(wnd)
            library.check_last_status_raise_on_error()

    count = property(_get_count)
