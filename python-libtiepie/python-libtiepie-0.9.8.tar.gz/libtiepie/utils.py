import datetime
import socket
import struct
from .const import *
from .types import *


def convert_version(value):
    """Convert UInt64/c_uint64 to Version object."""
    if value == 0:
        return None
    return Version(value >> 48, (value >> 32) & 0xffff, (value >> 16) & 0xffff, value & 0xffff)


def convert_date(value):
    """Convert UInt32/c_uint32 to datetime.date object."""
    if value == 0:
        return None
    return datetime.date(value >> 16, (value >> 8) & 0xff, value & 0xff)


def convert_tristate(value):
    if value == TRISTATE_TRUE:
        return Tristate(True)
    elif value == TRISTATE_FALSE:
        return Tristate(False)
    else:
        return Tristate(None)


def is_string(obj):
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)


def ipv4_str(value):
    return socket.inet_ntoa(struct.pack("!I", value))


def auto_resolution_mode_str(value):
    result = []
    for i in range(ARN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(AUTO_RESOLUTION_MODES[bit])

    return ', '.join(result)


def coupling_str(value):
    result = []
    for i in range(CKN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(COUPLINGS[bit])

    return ', '.join(result)


def clock_output_str(value):
    result = []
    for i in range(CON_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(CLOCK_OUTPUTS[bit])

    return ', '.join(result)


def clock_source_str(value):
    result = []
    for i in range(CSN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(CLOCK_SOURCES[bit])

    return ', '.join(result)


def connector_type_str(value):
    result = []
    for i in range(CONNECTORTYPE_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(CONNECTOR_TYPES[bit])

    return ', '.join(result)


def device_type_str(value):
    result = []
    for i in range(DEVICETYPE_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(DEVICE_TYPES[bit])

    return ', '.join(result)


def frequency_mode_str(value):
    result = []
    for i in range(FMN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(FREQUENCY_MODES[bit])

    return ', '.join(result)


def generator_mode_str(value):
    result = []
    for i in range(GMN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(GENERATOR_MODES[bit])

    return ', '.join(result)


def generator_status_str(value):
    result = []
    for i in range(GSN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(GENERATOR_STATUSS[bit])

    return ', '.join(result)


def interface_str(value):
    result = []
    for i in range(INTERFACE_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(INTERFACES[bit])

    return ', '.join(result)


def measure_mode_str(value):
    result = []
    for i in range(MMN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(MEASURE_MODES[bit])

    return ', '.join(result)


def server_error_str(value):
    return SERVER_ERRORS[value]


def server_status_str(value):
    return SERVER_STATUSS[value]


def signal_type_str(value):
    result = []
    for i in range(STN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(SIGNAL_TYPES[bit])

    return ', '.join(result)


def trigger_condition_str(value):
    result = []
    for i in range(TCN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(TRIGGER_CONDITIONS[bit])

    return ', '.join(result)


def trigger_kind_str(value):
    result = []
    for i in range(TKN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(TRIGGER_KINDS[bit])

    return ', '.join(result)


def trigger_level_mode_str(value):
    result = []
    for i in range(TLMN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(TRIGGER_LEVEL_MODES[bit])

    return ', '.join(result)


def trigger_output_event_str(value):
    result = []
    for i in range(TOEN_COUNT):
        bit = 1 << i
        if (value & bit) != 0:
            result.append(TRIGGER_OUTPUT_EVENTS[bit])

    return ', '.join(result)
