from ctypes import *
from .api import api
from .const import *
from .utils import *
from .library import library
from .object import Object


class Server(Object):
    """"""

    def __init__(self, handle):
        super(Server, self).__init__(handle)

    def __eq__(self, other):
        if type(self) is type(other):
            return self._handle == other._handle
        return NotImplemented

    def __ne__(self, other):
        if type(self) is type(other):
            return not self.__eq__(other)
        return NotImplemented

    def connect(self, asynchronous=False):
        """ Connect to a specified network instrument or instrument server.

        :param asynchronous: Connect asynchronously
        :returns: ``True`` if successful, ``False`` otherwise.
        .. versionadded:: 0.9
        """
        asynchronous = BOOL8_TRUE if asynchronous else BOOL8_FALSE
        result = api.SrvConnect(self._handle, asynchronous)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def disconnect(self, force=False):
        """ Disconnect from a specified network instrument or instrument server.

        :param force: If ``True`` all open devices are closed, if ``False`` remove only succeeds if no devices are open.
        :returns: ``True`` if successful, ``False`` otherwise.
        .. versionadded:: 0.9
        """
        force = BOOL8_TRUE if force else BOOL8_FALSE
        result = api.SrvDisconnect(self._handle, force)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def remove(self, force=False):
        """ Remove a specified specified network instrument or instrument server from the list of servers.

        :param force: If ``True`` all open devices are closed, if ``False`` remove only succeeds if no devices are open.
        :returns: ``True`` if successful, ``False`` otherwise.
        .. versionadded:: 0.9
        """
        force = BOOL8_TRUE if force else BOOL8_FALSE
        result = api.SrvRemove(self._handle, force)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def _get_status(self):
        """ Retrieve the status of a specified network instrument or instrument server. """
        value = api.SrvGetStatus(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_last_error(self):
        """ Last error from a specified network instrument or instrument server. """
        value = api.SrvGetLastError(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_url(self):
        """ URL of the specified network instrument or instrument server. """
        length = api.SrvGetURL(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.SrvGetURL(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_id(self):
        """ Id of the specified network instrument or instrument server. """
        length = api.SrvGetID(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.SrvGetID(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_ipv4_address(self):
        """ IPv4 address of the specified network instrument or instrument server. """
        value = api.SrvGetIPv4Address(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_ip_port(self):
        """ IP port number of the specified network instrument or instrument server. """
        value = api.SrvGetIPPort(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_name(self):
        """ Name of the specified network instrument or instrument server. """
        length = api.SrvGetName(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.SrvGetName(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_description(self):
        """ Description of the specified network instrument or instrument server. """
        length = api.SrvGetDescription(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.SrvGetDescription(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_version(self):
        """ Software version number of the specified network instrument or instrument server. """
        value = api.SrvGetVersion(self._handle)
        library.check_last_status_raise_on_error()
        return convert_version(value)

    def _get_version_extra(self):
        """ Software version postfix of the specified network instrument or instrument server. """
        length = api.SrvGetVersionExtra(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.SrvGetVersionExtra(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    status = property(_get_status)
    last_error = property(_get_last_error)
    url = property(_get_url)
    id = property(_get_id)
    ipv4_address = property(_get_ipv4_address)
    ip_port = property(_get_ip_port)
    name = property(_get_name)
    description = property(_get_description)
    version = property(_get_version)
    version_extra = property(_get_version_extra)
