from .api import api
from .const import *
from .utils import *
from .library import library
from .object import Object
from .triggerinputs import TriggerInputs
from .triggeroutputs import TriggerOutputs


class Device(Object):
    """"""

    def __init__(self, handle):
        super(Device, self).__init__(handle)
        self._trigger_inputs = TriggerInputs(handle)
        self._trigger_outputs = TriggerOutputs(handle)

    def _get_trigger_inputs(self):
        return self._trigger_inputs

    def _get_trigger_outputs(self):
        return self._trigger_outputs

    def _get_driver_version(self):
        """ Version number of the driver used by the device. """
        value = api.DevGetDriverVersion(self._handle)
        library.check_last_status_raise_on_error()
        return convert_version(value)

    def _get_firmware_version(self):
        """ Version number of the firmware used by the device. """
        value = api.DevGetFirmwareVersion(self._handle)
        library.check_last_status_raise_on_error()
        return convert_version(value)

    def _get_calibration_date(self):
        """ Calibration date of the device. """
        value = api.DevGetCalibrationDate(self._handle)
        library.check_last_status_raise_on_error()
        return convert_date(value)

    def _get_calibration_token(self):
        """ Calibration token of the device. """
        length = api.DevGetCalibrationToken(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.DevGetCalibrationToken(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_serial_number(self):
        """ Serial number of the device. """
        value = api.DevGetSerialNumber(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_ipv4_address(self):
        """ IPv4 address of the device. """
        value = api.DevGetIPv4Address(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_ip_port(self):
        """ IP port number of the device. """
        value = api.DevGetIPPort(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_product_id(self):
        """ Product id of the device. """
        value = api.DevGetProductId(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_vendor_id(self):
        """ Vendor id of the device. """
        value = api.DevGetVendorId(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_type(self):
        """ Device type. """
        value = api.DevGetType(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_name(self):
        """ Full name of the device. """
        length = api.DevGetName(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.DevGetName(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_name_short(self):
        """ Short name of the device. """
        length = api.DevGetNameShort(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.DevGetNameShort(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_name_shortest(self):
        """ Short name of the device without model postfix. """
        length = api.DevGetNameShortest(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.DevGetNameShortest(self._handle, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_has_battery(self):
        """ Check whether the device has a battery. """
        value = api.DevHasBattery(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_battery_charge(self):
        """ Get battery charge in percent. """
        value = api.DevGetBatteryCharge(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_battery_time_to_empty(self):
        """ Get battery time to empty in minutes. """
        value = api.DevGetBatteryTimeToEmpty(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_battery_time_to_full(self):
        """ Get battery time to full in minutes. """
        value = api.DevGetBatteryTimeToFull(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_is_battery_charger_connected(self):
        """ Check whether the battery charger is connected. """
        value = api.DevIsBatteryChargerConnected(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_battery_charging(self):
        """ Check whether the battery is charging. """
        value = api.DevIsBatteryCharging(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_is_battery_broken(self):
        """ Check whether the battery is broken. """
        value = api.DevIsBatteryBroken(self._handle)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def set_callback_removed(self, callback, data):
        """ Set a callback function which is called when the device is removed.

        :param callback: A pointer to the callback function. Use ``None`` to disable.
        :param data: Optional user data.
        """
        api.DevSetCallbackRemoved(self._handle, callback, data)
        library.check_last_status_raise_on_error()

    if platform.system() == 'Linux':
        def set_event_removed(self, event):
            """ Set an event file descriptor which is set when the device is removed.

            :param event: An event file descriptor. Use <tt><0</tt> to disable.
            """
            api.DevSetEventRemoved(self._handle, event)
            library.check_last_status_raise_on_error()

    if platform.system() == 'Windows':
        def set_event_removed(self, event):
            """ Set an event object handle which is set when the device is removed.

            :param event: A handle to the event object. Use ``None`` to disable.
            """
            api.DevSetEventRemoved(self._handle, event)
            library.check_last_status_raise_on_error()

        def set_message_removed(self, wnd, wparam, lparam):
            """ Set a window handle to which a #WM_LIBTIEPIE_DEV_REMOVED message is sent when the device is removed.

            :param wnd: A handle to the window whose window procedure is to receive the message. Use ``None`` to disable.
            :param wparam: Optional user value for the ``wParam`` parameter of the message.
            :param lparam: Optional user value for the ``lParam`` parameter of the message.
            """
            api.DevSetMessageRemoved(self._handle, wnd, wparam, lparam)
            library.check_last_status_raise_on_error()

    driver_version = property(_get_driver_version)
    firmware_version = property(_get_firmware_version)
    calibration_date = property(_get_calibration_date)
    calibration_token = property(_get_calibration_token)
    serial_number = property(_get_serial_number)
    ipv4_address = property(_get_ipv4_address)
    ip_port = property(_get_ip_port)
    product_id = property(_get_product_id)
    vendor_id = property(_get_vendor_id)
    type = property(_get_type)
    name = property(_get_name)
    name_short = property(_get_name_short)
    name_shortest = property(_get_name_shortest)
    has_battery = property(_get_has_battery)
    battery_charge = property(_get_battery_charge)
    battery_time_to_empty = property(_get_battery_time_to_empty)
    battery_time_to_full = property(_get_battery_time_to_full)
    is_battery_charger_connected = property(_get_is_battery_charger_connected)
    is_battery_charging = property(_get_is_battery_charging)
    is_battery_broken = property(_get_is_battery_broken)
    trigger_inputs = property(_get_trigger_inputs)
    trigger_outputs = property(_get_trigger_outputs)
