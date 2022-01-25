from array import array
from ctypes import create_string_buffer
from .api import api
from .const import *
from .utils import *
from .library import library
from .exceptions import InvalidValueError
from .oscilloscope import Oscilloscope
from .generator import Generator
from .i2chost import I2CHost
from .server import Server


class DeviceListItem(object):
    """"""

    def __init__(self, serial_number):
        self._serial_number = serial_number

    def open_device(self, device_type):
        """ Open a device .

        :param device_type: A device type.
        :returns: Instance of :class:`.Oscilloscope`, :class:`.Generator` or :class:`.I2CHost`.
        """
        result = api.LstOpenDevice(IDKIND_SERIALNUMBER, self._serial_number, device_type)
        library.check_last_status_raise_on_error()
        return library.create_object(result)

    def open_oscilloscope(self):
        """ Open an oscilloscope .

        :returns: Instance of :class:`.Oscilloscope`.
        """
        result = api.LstOpenOscilloscope(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return Oscilloscope(result)

    def open_generator(self):
        """ Open a generator .

        :returns: Instance of :class:`.Generator`.
        """
        result = api.LstOpenGenerator(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return Generator(result)

    def open_i2c_host(self):
        """ Open an I2C host .

        :returns: Instance of :class:`.I2CHost`.
        """
        result = api.LstOpenI2CHost(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return I2CHost(result)

    def can_open(self, device_type):
        """ Check whether the listed device can be opened.

        :param device_type: A device type.
        :returns: ``True`` if the device can be opened or ``False`` if not.
        """
        result = api.LstDevCanOpen(IDKIND_SERIALNUMBER, self._serial_number, device_type)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def _get_product_id(self):
        """ Product id. """
        value = api.LstDevGetProductId(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return value

    def _get_vendor_id(self):
        """ Vendor id. """
        value = api.LstDevGetVendorId(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return value

    def _get_name(self):
        """ Full name. """
        length = api.LstDevGetName(IDKIND_SERIALNUMBER, self._serial_number, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.LstDevGetName(IDKIND_SERIALNUMBER, self._serial_number, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_name_short(self):
        """ Short name. """
        length = api.LstDevGetNameShort(IDKIND_SERIALNUMBER, self._serial_number, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.LstDevGetNameShort(IDKIND_SERIALNUMBER, self._serial_number, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_name_shortest(self):
        """ Short name wihout model postfix. """
        length = api.LstDevGetNameShortest(IDKIND_SERIALNUMBER, self._serial_number, None, 0)
        library.check_last_status_raise_on_error()
        buf = create_string_buffer(length + 1)
        api.LstDevGetNameShortest(IDKIND_SERIALNUMBER, self._serial_number, buf, length)
        library.check_last_status_raise_on_error()
        return buf.value.decode('utf-8')

    def _get_driver_version(self):
        """ Version number of the driver currently used. """
        value = api.LstDevGetDriverVersion(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return convert_version(value)

    def _get_recommended_driver_version(self):
        """ Version number of the recommended driver. """
        value = api.LstDevGetRecommendedDriverVersion(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return convert_version(value)

    def _get_firmware_version(self):
        """ Version number of the firmware currently used. """
        value = api.LstDevGetFirmwareVersion(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return convert_version(value)

    def _get_recommended_firmware_version(self):
        """ Version number of the recommended firmware. """
        value = api.LstDevGetRecommendedFirmwareVersion(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return convert_version(value)

    def _get_calibration_date(self):
        """ Calibration date. """
        value = api.LstDevGetCalibrationDate(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return convert_date(value)

    def _get_serial_number(self):
        """ Serial number. """
        value = api.LstDevGetSerialNumber(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return value

    def _get_ipv4_address(self):
        """ IPv4 address. """
        value = api.LstDevGetIPv4Address(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return value

    def _get_ip_port(self):
        """ IP port number. """
        value = api.LstDevGetIPPort(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return value

    def _get_has_server(self):
        """ Check whether the listed device is connected to a server. """
        value = api.LstDevHasServer(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _get_server(self):
        """ Server handle of the server the listed device is connected to. """
        value = api.LstDevGetServer(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return Server(value)

    def _get_types(self):
        """ Device types. """
        value = api.LstDevGetTypes(IDKIND_SERIALNUMBER, self._serial_number)
        library.check_last_status_raise_on_error()
        return value

    def _get_contained_serial_numbers(self):
        """ Serial numbers of the individual devices contained in a combined device. """
        count = api.LstDevGetContainedSerialNumbers(IDKIND_SERIALNUMBER, self._serial_number, None, 0)
        library.check_last_status_raise_on_error()
        values = (c_uint32 * count)()
        api.LstDevGetContainedSerialNumbers(IDKIND_SERIALNUMBER, self._serial_number, values, count)
        library.check_last_status_raise_on_error()
        return array('L', values)

    product_id = property(_get_product_id)
    vendor_id = property(_get_vendor_id)
    name = property(_get_name)
    name_short = property(_get_name_short)
    name_shortest = property(_get_name_shortest)
    driver_version = property(_get_driver_version)
    recommended_driver_version = property(_get_recommended_driver_version)
    firmware_version = property(_get_firmware_version)
    recommended_firmware_version = property(_get_recommended_firmware_version)
    calibration_date = property(_get_calibration_date)
    serial_number = property(_get_serial_number)
    ipv4_address = property(_get_ipv4_address)
    ip_port = property(_get_ip_port)
    has_server = property(_get_has_server)
    server = property(_get_server)
    types = property(_get_types)
    contained_serial_numbers = property(_get_contained_serial_numbers)
