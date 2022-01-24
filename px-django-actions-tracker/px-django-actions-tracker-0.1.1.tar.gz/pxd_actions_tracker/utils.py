import ast
import ipaddress
from typing import Any, Optional, TypeVar

from .conf import settings


__all__ = (
    'is_list',
    'is_dict',
    'clean_data',
    'get_ip_address',
)

T = TypeVar('T')


def is_list(value) -> bool:
    return isinstance(value, (list, tuple))


def is_dict(value) -> bool:
    return isinstance(value, dict)


def clean_data(
    data: T,
    sensitive_fields: Optional[set] = None,
    sensitive_placeholder: Optional[str] = None,
) -> T:
    """Replaces sensitive information from data."""
    sensitive_fields = (
        settings.SENSITIVE_FIELDS
        if sensitive_fields is None else
        sensitive_fields
    )
    sensitive_placeholder = (
        settings.SENSITIVE_PLACEHOLDER
        if sensitive_placeholder is None else
        sensitive_placeholder
    )

    if isinstance(data, bytes):
        data = data.decode(errors='replace')

    if is_list(data):
        return [clean_data(d, sensitive_fields=sensitive_fields) for d in data]

    if is_dict(data):
        data = dict(data)

        for key, value in data.items():
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                pass

            if is_list(value) or is_dict(value):
                data[key] = clean_data(
                    value, sensitive_fields=sensitive_fields
                )

            if key.lower() in sensitive_fields:
                data[key] = sensitive_placeholder

    return data


def get_ip_address(request):
    """Get the remote ip address the request was generated from. """
    address = request.META.get('HTTP_X_FORWARDED_FOR', None)

    if address:
        address = address.split(',')[0]
    else:
        address = request.META.get('REMOTE_ADDR', '')

    # Account for IPv4 and IPv6 addresses, each possibly with port appended.
    # Possibilities are:
    # <ipv4 address>
    # <ipv6 address>
    # <ipv4 address>:port
    # [<ipv6 address>]:port
    # Note that ipv6 addresses are colon separated hex numbers
    possibles = (address.lstrip('[').split(']')[0], address.split(':')[0])

    for addr in possibles:
        try:
            return str(ipaddress.ip_address(addr))
        except ValueError:
            pass

    return address
