"""Arduino API wrapper.
"""

from . import serial, tlv, tracing


class ArduinoException(Exception):
    """Base class for Arduino-related errors."""
    pass


class DeviceError(ArduinoException):
    """An error reported by the Arduino device."""
    pass


class ProtocolError(ArduinoException):
    """An error in the remote Arduino protocol."""
    pass


def command(*args, **kwargs):
    """Execute a remote Arduino command.

    See Link.command() for parameter details.
    """

    return serial.Link.get().command(*args, **kwargs)


def protocol_version():
    """What version of the serial protocol are we speaking?"""

    return serial.Link.get().version
