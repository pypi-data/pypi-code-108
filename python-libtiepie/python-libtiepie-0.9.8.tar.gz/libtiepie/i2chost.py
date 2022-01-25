from array import array
from ctypes import *
from .api import api
from .const import *
from .library import library
from .device import Device


class I2CHost(Device):
    """"""

    def __init__(self, handle):
        super(I2CHost, self).__init__(handle)

    def is_internal_address(self, address):
        """ Check whether an address is used internally.

        :param address: An I2C device address.
        :returns: ``True`` if the address is used internally, ``False`` otherwise.
        """
        result = api.I2CIsInternalAddress(self._handle, address)
        library.check_last_status_raise_on_error()
        return result != BOOL8_FALSE

    def _get_internal_addresses(self):
        """ :class:`array.array` of addresses which are used internally. """
        count = api.I2CGetInternalAddresses(self._handle, None, 0)
        library.check_last_status_raise_on_error()
        values = (c_uint16 * count)()
        api.I2CGetInternalAddresses(self._handle, values, count)
        library.check_last_status_raise_on_error()
        return array('H', values)

    def read(self, address, count, stop=True):
        """ Read data from a specified address on the I2C bus.

        :param address: The I2C address to read from.
        :param count: Number of bytes to read.
        :param stop: Indicates whether an I2C stop is generated after the transaction, when ``True``, an I2C stop is generated, when ``False`` not.
        :returns: :class:`array.array` of read bytes.
        """
        buffer = (c_ubyte * count)()
        api.I2CRead(self._handle, address, pointer(buffer), count, BOOL8_TRUE if stop else BOOL8_FALSE)
        library.check_last_status_raise_on_error()
        return array('B', buffer)

    def read_byte(self, address):
        """ Read one byte from a specified address on the I2C bus.

        :param address: The I2C address to read from.
        :returns: The read value.
        """
        value = c_ubyte()
        api.I2CReadByte(self._handle, address, pointer(value))
        library.check_last_status_raise_on_error()
        return value.value

    def read_word(self, address):
        """ Read one word from a specified address on the I2C bus.

        :param address: The I2C address to read from.
        :returns: The read value.
        """
        value = c_ushort()
        api.I2CReadWord(self._handle, address, pointer(value))
        library.check_last_status_raise_on_error()
        return value.value

    def write(self, address, buffer, stop=True):
        """ Write data to a specified address on the I2C bus.

        :param address: The I2C address to write to.
        :param buffer: :class:`array.array` of bytes to write.
        :param stop: Indicates whether an I2C stop is generated after the transaction, when ``True``, an I2C stop is generated, when ``False`` not.
        """
        if isinstance(buffer, array) and buffer.typecode == 'B':
            buffer_ptr = c_void_p(buffer.buffer_info()[0])
            buffer_ptr.__ref = buffer
            api.I2CWrite(self._handle, address, buffer_ptr, len(buffer), BOOL8_TRUE if stop else BOOL8_FALSE)
            library.check_last_status_raise_on_error()
        else:
            raise Exception('Invalid data, must be array.array with typecode = `B`')

    def write_byte(self, address, value):
        """ Write one byte to a specified address on the I2C bus.

        :param address: The I2C address to write to.
        :param value: The byte value to write.
        """
        api.I2CWriteByte(self._handle, address, value)
        library.check_last_status_raise_on_error()

    def write_byte_byte(self, address, value1, value2):
        """ Write two bytes to a specified address on the I2C bus.

        :param address: The I2C address to write to.
        :param value1: The first byte value to write.
        :param value2: The second byte value to write.
        """
        api.I2CWriteByteByte(self._handle, address, value1, value2)
        library.check_last_status_raise_on_error()

    def write_byte_word(self, address, value1, value2):
        """ Write one byte and one word to a specified address on the I2C bus.

        :param address: The I2C address to write to.
        :param value1: The byte value to write.
        :param value2: The word value to write.
        """
        api.I2CWriteByteWord(self._handle, address, value1, value2)
        library.check_last_status_raise_on_error()

    def write_word(self, address, value):
        """ Write one word to a specified address on the I2C bus.

        :param address: The I2C address to write to.
        :param value: The word value to write.
        """
        api.I2CWriteWord(self._handle, address, value)
        library.check_last_status_raise_on_error()

    def write_read(self, address, write_buffer, read_count):
        """ Write and read data to/from to a specified address on the I2C bus.

        :param address: The I2C address to write to.
        :param write_buffer: :class:`array.array` of bytes to write.
        :param read_count: Number of bytes to read.
        :returns: :class:`array.array` of read bytes.
        .. versionadded:: 0.6
        """
        if isinstance(write_buffer, array) and write_buffer.typecode == 'B':
            write_buffer_ptr = c_void_p(write_buffer.buffer_info()[0])
            write_buffer_ptr.__ref = write_buffer
            read_buffer = (c_ubyte * read_count)()
            api.I2CWriteRead(self._handle, address, write_buffer_ptr, len(write_buffer), pointer(read_buffer), read_count)
            library.check_last_status_raise_on_error()
            return array('B', read_buffer)
        else:
            raise Exception('Invalid data, must be array.array with typecode = `B`')

    def _get_speed_max(self):
        """ Maximum clock speed on the I2C bus. """
        value = api.I2CGetSpeedMax(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _get_speed(self):
        """ Current clock speed on the I2C bus. """
        value = api.I2CGetSpeed(self._handle)
        library.check_last_status_raise_on_error()
        return value

    def _set_speed(self, value):
        api.I2CSetSpeed(self._handle, value)
        library.check_last_status_raise_on_error()

    def verify_speed(self, speed):
        """ Verify if a clock speed on the I2C bus can be set, without actually setting the hardware.

        :param speed: The requested I2C clock speed in Hz.
        :returns: The I2C clock speed that would have been set, in Hz.
        """
        result = api.I2CVerifySpeed(self._handle, speed)
        library.check_last_status_raise_on_error()
        return result

    internal_addresses = property(_get_internal_addresses)
    speed_max = property(_get_speed_max)
    speed = property(_get_speed, _set_speed)
