import logging

from collections import OrderedDict as OrderedDict
from typing import Dict, FrozenSet, List, Optional, Set, Tuple, Union

from chardet import detect as detect_encoding

LOG = logging.getLogger(__name__)
REDACT_TYPES = Union[Dict, FrozenSet, List, OrderedDict, Set, str, bytes, Tuple]
"""Object types supported by the redact method."""


def decode_bytes(value: bytes, encoding: Optional[str] = None) -> str:
    """
    Attempt to decode bytes into a string value.

    Uses chardet to detect encoding. This is in place because there were checks in the old logging system that implied
    that messages could come in as utf-8 signed with a byte order mark - this is also called `utf-8-sig`. Here is the
    problem; suppose you have some bytes that were encoded as `utf-8-sig` and you tried to decode it  as `utf-8`; this
    will NOT raise a UnicodeDecodeError, but that first byte ends up as a weird unprintable unicode character::

        >>> d = "foo".encode("utf-8-sig")
        >>> d.decode("utf-8-sig")
        'foo'
        >>> d.decode("utf-8")
        '\ufefffoo'
        >>>

    For simplicity, we detect the encoding in advance. Low confidence detection values are attempted as utf-8 and
    fallback to the detected encoding in the case of a UnicodeDecodeError.
    """
    if encoding is None:
        detect_info = detect_encoding(value)
        if detect_info["confidence"] == 1.0:
            return value.decode(detect_info["encoding"])
        else:
            # chardet has issue with some simple utf-8 strings, misdetecting as Windows-1252, try
            # decoding as utf-8 since that's likely the safest option anyway. If that fails, fallback
            # to the detected encoding
            try:
                return value.decode('utf-8')
            except UnicodeDecodeError:
                return value.decode(detect_info["encoding"])
    else:
        return value.decode(encoding)


def redact(value: REDACT_TYPES, replace_map: Dict[str, str]) -> REDACT_TYPES:
    """
    Redact senstive information from a given value.

    This method operates recursively, descending through most common mapping and sequential data structures
    it finds. The replacement map should be a mapping where they key is the text to redact and the value is
    what to replace it with. i.e. ::

        >>> replacement_map = {
        >>>     "secretpassword": "<PASSWORD>",
        >>>     "bMzkiqnyFgmqhKfWMckqLEd1": "<DOCKER-PASSWORD>",
        >>> }
        >>>

    """
    if isinstance(value, str):
        for secret, replacement in replace_map.items():
            value = value.replace(secret, replacement)
        return value

    if isinstance(value, bytes):
        encoding = detect_encoding(value)["encoding"]
        str_value = value.decode(encoding)
        for secret, replacement in replace_map.items():
            str_value = value.replace(secret, replacement)
        return str_value.encode(encoding)

    if isinstance(value, frozenset):
        return frozenset((redact(x, replace_map) for x in value))

    if isinstance(value, set):
        return {(redact(x, replace_map) for x in value)}

    if isinstance(value, list):
        return [redact(x, replace_map) for x in value]

    if isinstance(value, tuple):
        return tuple((redact(x, replace_map) for x in value))

    if isinstance(value, OrderedDict):
        new_dict = OrderedDict()
        for k, v in value.items():
            new_dict[redact(k, replace_map)] = redact(v, replace_map)
        return new_dict

    if isinstance(value, dict):
        value = {redact(k, replace_map): redact(v, replace_map) for k, v in value.items()}

    return value
