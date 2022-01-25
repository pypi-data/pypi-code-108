from ctypes import c_uint32
from .api import api
from .const import *
from .library import library
from .devicelistitem import DeviceListItem
from .exceptions import InvalidDeviceIndexError


class DeviceList(object):
    """"""

    def __getitem__(self, index):
        try:
            return self.get_item_by_index(index)
        except (InvalidDeviceIndexError):
            raise IndexError()

    def __len__(self):
        return self.count

    def get_item_by_index(self, index):
        serial_number = api.LstDevGetSerialNumber(IDKIND_INDEX, index)
        library.check_last_status_raise_on_error()
        return DeviceListItem(serial_number)

    def get_item_by_product_id(self, pid):
        serial_number = api.LstDevGetSerialNumber(IDKIND_PRODUCTID, pid)
        library.check_last_status_raise_on_error()
        return DeviceListItem(serial_number)

    def get_item_by_serial_number(self, serial_number):
        serial_number = api.LstDevGetSerialNumber(IDKIND_SERIALNUMBER, serial_number)
        library.check_last_status_raise_on_error()
        return DeviceListItem(serial_number)

    def update(self):
        api.LstUpdate()
        library.check_last_status_raise_on_error()

    def _get_count(self):
        """ Number of devices in the device list. """
        value = api.LstGetCount()
        library.check_last_status_raise_on_error()
        return value

    def create_combined_device(self, devices):
        """ Create a combined instrument.

        :param device: :class:`list` of Device instances.
        :returns: Device list item of combined device.
        """
        handles = (c_uint32 * len(devices))()
        i = 0
        for device in devices:
            handles[i] = device._handle
            i += 1
        serial_number = api.LstCreateCombinedDevice(handles, len(handles))
        library.check_last_status_raise_on_error()
        return DeviceListItem(serial_number)

    def create_and_open_combined_device(self, devices):
        """ Create and open a combined instrument.

        :param device: :class:`list` of Device instances.
        :returns: Instance of combined device.
        """
        item = self.create_combined_device(devices)
        return item.open_device(item.types)

    def remove_device(self, serial_number, force=False):
        """ Remove an instrument from the device list so it can be used by other applications.

        :param serial_number: Serial number of the device to remove.
        :param force: Force the removal, even when the device is currenty opened.
        """
        if force:
            api.LstRemoveDeviceForce(serial_number)
        else:
            api.LstRemoveDevice(serial_number)
        library.check_last_status_raise_on_error()

    def set_callback_device_added(self, callback, data):
        """ Set a callback function which is called when a device is added to the device list.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.LstSetCallbackDeviceAdded(callback, data)
        library.check_last_status_raise_on_error()

    def set_callback_device_removed(self, callback, data):
        """ Set a callback function which is called when a device is removed from the device list.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.LstSetCallbackDeviceRemoved(callback, data)
        library.check_last_status_raise_on_error()

    def set_callback_device_can_open_changed(self, callback, data):
        """ Set a callback function which is called when the device can open property changes.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        .. versionadded:: 0.6
        """
        api.LstSetCallbackDeviceCanOpenChanged(callback, data)
        library.check_last_status_raise_on_error()

    if platform.system() == 'Linux':
        def set_event_device_added(self, event):
            """ Set an event file descriptor which is set when a device is added to the device list.

            :param event: An event file descriptor. Use ``<0`` to disable.
            """
            api.LstSetEventDeviceAdded(event)
            library.check_last_status_raise_on_error()

        def set_event_device_removed(self, event):
            """ Set an event file descriptor which is set when a device is removed from the device list.

            :param event: an event file descriptor. Use ``<0`` to disable.
            """
            api.LstSetEventDeviceRemoved(event)
            library.check_last_status_raise_on_error()

        def set_event_device_can_open_changed(self, event):
            """ Set an event file descriptor which is set when the device can open property changes.

            :param event: an event file descriptor. Use ``<0`` to disable.
            .. versionadded:: 0.6
            """
            api.LstSetEventDeviceCanOpenChanged(event)
            library.check_last_status_raise_on_error()

    if platform.system() == 'Windows':
        def set_event_device_added(self, event):
            """ Set an event object handle which is set when a device is added to the device list.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.LstSetEventDeviceAdded(event)
            library.check_last_status_raise_on_error()

        def set_event_device_removed(self, event):
            """ Set an event object handle which is set when a device is removed from the device list.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.LstSetEventDeviceRemoved(event)
            library.check_last_status_raise_on_error()

        def set_event_device_can_open_changed(self, event):
            """ Set an event object handle which is set when the device can open property changes.

            :param event: A handle to the event object. Use ``None`` to disable.
            .. versionadded:: 0.6
            """
            api.LstSetEventDeviceCanOpenChanged(event)
            library.check_last_status_raise_on_error()

        def set_message_device_added(self, wnd):
            """ Set a window handle to which a #WM_LIBTIEPIE_LST_DEVICEADDED message is sent when a device is added to the device list.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            """
            api.LstSetMessageDeviceAdded(wnd)
            library.check_last_status_raise_on_error()

        def set_message_device_removed(self, wnd):
            """ Set a window handle to which a #WM_LIBTIEPIE_LST_DEVICEREMOVED message is sent when a device is removed from the device list.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            """
            api.LstSetMessageDeviceRemoved(wnd)
            library.check_last_status_raise_on_error()

        def set_message_device_can_open_changed(self, wnd):
            """ Set a window handle to which a #WM_LIBTIEPIE_LST_DEVICEREMOVED message is sent when the device can open property changes.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            .. versionadded:: 0.6
            """
            api.LstSetMessageDeviceCanOpenChanged(wnd)
            library.check_last_status_raise_on_error()

    count = property(_get_count)


device_list = DeviceList()
