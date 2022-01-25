#!/usr/bin/python
# -*-coding:Utf-8 -*
#
# disable naming convention issue
# pylint: disable=C0103
##########################################################
"""
Exceptions for the SOLIDServer modules
"""

# import logging

__all__ = [
    "SDSError",

    "SDSAuthError",
    "SDSEmptyError",
    "SDSInitError",
    "SDSRequestError",
    "SDSServiceError",

    "SDSSpaceError",

    "SDSDeviceError", "SDSDeviceNotFoundError",
    "SDSDeviceIfError", "SDSDeviceIfNotFoundError",
    "SDSNetworkError", "SDSNetworkNotFoundError",
    "SDSIpAddressError", "SDSIpAddressNotFoundError",

    "SDSDNSError", "SDSDNSAlreadyExistingError",
    "SDSDNSCredentialsError",
]


# --------------------------------------------------------------------------
class SDSError(Exception):
    """ generic class for any exception in SOLIDServer communication """

    def __init__(self, message=""):
        super().__init__()
        self.message = message

    def __str__(self):
        return f"{self.message}"


class SDSInitError(SDSError):
    """ raised when action on non initialized SSD connection """

    def __init__(self, message=""):
        super().__init__(f"[init] {message}")


class SDSServiceError(SDSError):
    """ raised on unknown service """

    def __init__(self, service_name, message=""):
        super().__init__(message)
        self.service = service_name

    def __str__(self):
        return f"{self.message} on service {self.service}"


class SDSRequestError(SDSError):
    """ raised when urllib request is failing """

    def __init__(self, method, url, headers, message=""):
        super().__init__(message)
        self.method = method
        self.url = url
        self.headers = headers

    def __str__(self):
        return f"{self.message} with {self.method} {self.url}"


# this class cannot be tests with non connected coverage
class SDSAuthError(SDSError):   # pragma: no cover
    """ raised when auth on request is wrong """

    def __init__(self, message=""):
        super().__init__(f"authent: {message}")


# this class cannot be tests with non connected coverage
class SDSEmptyError(SDSError):   # pragma: no cover
    """ raised when empty answer """

    def __init__(self, message=""):
        super().__init__(f"empty answer: {message}")


class SDSSpaceError(SDSError):   # pragma: no cover
    """ raised when error on space """

    def __init__(self, message=""):
        super().__init__(f"space error: {message}")


class SDSDeviceError(SDSError):   # pragma: no cover
    """ raised when error on device """

    def __init__(self, message=""):
        message = f"device error: {message}"
        super().__init__(message)


class SDSDeviceNotFoundError(SDSError):   # pragma: no cover
    """ raised when device not found """

    def __init__(self, message=""):
        message = f"device not found: {message}"
        super().__init__(message)


class SDSDeviceIfError(SDSError):   # pragma: no cover
    """ raised when error on device interface """

    def __init__(self, message=""):
        message = f"device interface error: {message}"
        super().__init__(message)


class SDSDeviceIfNotFoundError(SDSError):   # pragma: no cover
    """ raised when device interface not found """

    def __init__(self, message=""):
        message = f"device interface not found: {message}"
        super().__init__(message)


class SDSNetworkError(SDSError):   # pragma: no cover
    """ raised when error on network """

    def __init__(self, message=""):
        message = f"network error: {message}"
        super().__init__(message)


class SDSNetworkNotFoundError(SDSError):   # pragma: no cover
    """ raised when network not found """

    def __init__(self, message=""):
        message = f"network not found: {message}"
        super().__init__(message)


class SDSIpAddressError(SDSError):   # pragma: no cover
    """ raised when error on ip address """

    def __init__(self, message=""):
        message = f"ip error: {message}"
        super().__init__(message)


class SDSIpAddressNotFoundError(SDSError):   # pragma: no cover
    """ raised when ip address not found """

    def __init__(self, message=""):
        message = f"ip not found: {message}"
        super().__init__(message)


class SDSDNSError(SDSError):   # pragma: no cover
    """ raised when dns server error """

    def __init__(self, message=""):
        message = f"DNS server error: {message}"
        super().__init__(message)


class SDSDNSAlreadyExistingError(SDSDNSError):   # pragma: no cover
    """ raised when dns server is already existing """

    def __init__(self, message=""):
        message = f"DNS server already existing: {message}"
        super().__init__(message)


class SDSDNSCredentialsError(SDSDNSError):   # pragma: no cover
    """ raised on dns server connexion error  """

    def __init__(self, message=""):
        message = f"DNS server credentials: {message}"
        super().__init__(message)
