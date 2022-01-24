#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""

"""
import logging
import socket
from ipaddress import ip_address, IPv4Address, IPv6Address
from logging import Logger
from typing import (
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import numpy as np

from hvl_ccb.utils.typing import Number


def validate_number(
    x_name: str,
    x: object,
    limits: Optional[Tuple] = (None, None),
    number_type: Union[Type[Number], Tuple[Type[Number], ...]] = (int, float),
    logger: Optional[Logger] = None,
) -> None:
    """
    Validate if given input `x` is a number of given `number_type` type, with value
    between given `limits[0]` and `limits[1]` (inclusive), if not `None`.
    For array-like objects (npt.NDArray, List, Tuple, Dict) it is checked if all
    elements are within the limits and have the correct type.

    :param x_name: string name of the validate input, use for the error message
    :param x: an input object to validate as number of given type within given range
    :param logger: logger of the calling submodule
    :param limits: [lower, upper] limit, with `None` denoting no limit: [-inf, +inf]
    :param number_type: expected type or tuple of types of a number,
        by default `(int, float)`
    :raises TypeError: when the validated input does not have expected type
    :raises ValueError: when the validated input has correct number type but is not
        within given range
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if limits is None:
        limits = (-np.inf, np.inf)
    if limits[0] is None:
        limits = (-np.inf, limits[1])
    if limits[1] is None:
        limits = (limits[0], np.inf)

    data_type = type(x)
    if not isinstance(number_type, Sequence):
        number_type = (number_type,)

    if isinstance(x, (float, int)):
        if not isinstance(x, number_type):
            msg = (
                f"{x_name} = {x} has to be of type "
                f"{' or '.join(nt.__name__ for nt in number_type)}"
            )
            logger.error(msg)
            raise TypeError(msg)
    elif isinstance(x, (list, tuple, dict, np.ndarray)):
        if isinstance(x, dict):
            x = np.asarray(list(x.values()))
        x = np.asarray(x)
        if x.dtype not in number_type:
            msg = (
                f"{x_name} = {x} needs to include only numbers type "
                f"{' or '.join(nt.__name__ for nt in number_type)}"
            )
            logger.error(msg)
            raise TypeError(msg)
    else:
        msg = (
            f"{x_name} = {x} must be an Integer, a Float, a Tuple, a List, "
            f"a Dictionary or a Numpy array, but the received type is {data_type}."
        )
        logger.error(msg)
        raise TypeError(msg)

    if np.any(x < limits[0]) or np.any(x > limits[1]):
        if np.isinf(limits[0]):
            suffix = f"less or equal than {limits[1]}"
        elif np.isinf(limits[1]):
            suffix = f"greater or equal than {limits[0]}"
        else:
            suffix = f"between {limits[0]} and {limits[1]} inclusive"
        msg = f"{x_name} = {x} has to be {suffix}"
        logger.error(msg)
        raise ValueError(msg)


def validate_bool(x_name: str, x: object, logger: Optional[Logger] = None) -> None:
    """
    Validate if given input `x` is a `bool`.

    :param x_name: string name of the validate input, use for the error message
    :param x: an input object to validate as boolean
    :param logger: logger of the calling submodule
    :raises TypeError: when the validated input does not have boolean type
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    if not isinstance(x, bool):
        msg = f"{x_name} = {x} has to of type bool"
        logger.error(msg)
        raise TypeError(msg)


def validate_and_resolve_host(
        host: Union[str, IPv4Address, IPv6Address],
        logger: Optional[Logger] = None
) -> str:
    if logger is None:
        logger = logging.getLogger(__name__)
    if host is None:
        msg = "A host has to be provided."
        logger.error(msg)
        raise AttributeError(msg)
    if isinstance(host, (IPv4Address, IPv6Address)):
        host = str(host)
    else:
        try:
            host = str(ip_address(host))
        except ValueError:
            try:
                host = socket.gethostbyname(host)
            except (socket.gaierror, UnicodeError):
                # UnicodeError: "192..168.01"
                # socket.gaierror: "192.168.0.1000"
                # socket.gaierror: "itet-hvl-01"
                msg = (
                    "The value of host is neither an IPv4 nor an IPv6 address nor a "
                    f"hostname that can be resolved. The received value is: '{host}'."
                )
                logger.error(msg)
                raise ValueError(msg)
    return str(host)


def validate_tcp_port(port: int, logger: Optional[Logger] = None):
    if logger is None:
        logger = logging.getLogger(__name__)
    if port is None:
        msg = "A port has to be provided."
        logger.error(msg)
        raise AttributeError(msg)
    # TCP ports are in the range between and including 0 and (2**16)-1, but 0 is
    # reserved and shall not be used
    validate_number("port", port, (1, 2**16-1), int, logger)
