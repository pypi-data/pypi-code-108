"""Module containing the exception class for gtunrealdevice."""


class WrapperError(Exception):
    """Use to capture error for using invalid decorator."""


class DevicesInfoError(Exception):
    """Use to capture devices info"""


class URDeviceError(Exception):
    """Use to capture error for creating GTUnrealDevice."""


class URDeviceConnectionError(URDeviceError):
    """Use to capture error when GTUnrealDevice establishes connection."""


class URDeviceOfflineError(URDeviceError):
    """Use to capture error when GTUnrealDevice is offline."""
