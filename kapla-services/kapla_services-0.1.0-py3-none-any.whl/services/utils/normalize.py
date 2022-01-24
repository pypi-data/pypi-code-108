from __future__ import annotations

from typing import Optional, Union


def normalize_header_key(
    value: Union[str, bytes],
    lower: bool = True,
    encoding: Optional[str] = None,
) -> bytes:
    """
    Coerce str/bytes into a strictly byte-wise HTTP header key.
    """
    if isinstance(value, bytes):
        bytes_value = value
    else:
        bytes_value = value.encode(encoding or "utf-8")

    return bytes_value.lower() if lower else bytes_value


def normalize_header_value(
    value: Union[str, bytes], encoding: Optional[str] = None
) -> bytes:
    """
    Coerce str/bytes into a strictly byte-wise HTTP header value.
    """
    if isinstance(value, bytes):
        return value
    return value.encode(encoding or "utf-8")
