# -*- coding: utf-8 -*-
"""Module implementing helper functions for handling protocol data units
"""
# import basic stuff
import struct
from typing import Tuple

# import own stuff
import tlsmate.tls as tls

# import other stuff


def pack_uint8(val: int) -> bytes:
    """Packs a uint8 value into a byte object.

    Arguments:
        val: The value to pack.

    Returns:
        The bytes object representing the value in network order (big endian).

    Raises:
        ValueError: If the value cannot be represented in one byte.
    """

    if val > 0xFF:
        raise ValueError(f"Cannot pack {val} into 1 byte")

    return struct.pack("!B", val)


def pack_uint16(val: int) -> bytes:
    """Packs a uint16 value into a byte object.

    Arguments:
        val: The value to pack.

    Returns:
        The bytes object representing the value in network order (big endian).

    Raises:
        ValueError: If the value cannot be represented in two bytes.
    """

    if val > 0xFFFF:
        raise ValueError(f"Cannot pack {val} into 2 bytes")

    return struct.pack("!H", val)


def pack_uint24(val: int) -> bytes:
    """Packs a uint24 value into a byte object.

    Arguments:
        val: The value to pack.

    Returns:
        The bytes object representing the value in network order (big endian).

    Raises:
        ValueError: If the value cannot be represented in three bytes.
    """

    if val > 0xFFFFFF:
        raise ValueError(f"Cannot pack {val} into 3 bytes")

    return struct.pack("!I", val)[1:]


def pack_uint32(val: int) -> bytes:
    """Packs a uint32 value into a byte object.

    Arguments:
        val: The value to pack.

    Returns:
        The bytes object representing the value in network order (big endian).

    Raises:
        ValueError: If the value cannot be represented in four bytes.
    """

    if val > 0xFFFFFFFF:
        raise ValueError(f"Cannot pack {val} into 4 bytes")

    return struct.pack("!I", val)


def pack_uint64(val: int) -> bytes:
    """Packs a uint64 value into a byte object.

    Arguments:
        val: The value to pack.

    Returns:
        The bytes object representing the value in network order (big endian).

    Raises:
        ValueError: If the value cannot be represented in eight bytes.
    """

    if val > 0xFFFFFFFFFFFFFFFF:
        raise ValueError(f"Cannot pack {val} into 8 bytes")

    return struct.pack("!Q", val)


def pack_str(string: str) -> bytes:
    """Packs a string into a byte object.

    Arguments:
        string: The string to pack.

    Returns:
        The bytes object representing the string in network order (big endian).
    """

    return bytes(map(ord, string))


def unpack_uint8(data: bytes, offset: int) -> Tuple[int, int]:
    """Unpacks a value from a given an buffer.

    Arguments:
        data: The buffer to unpack from.
        offset: The offset within the buffer.

    Returns:
        The tuple with the result. The first entry is the value that has been
        unpacked, the second one is the new offset in the buffer, i.e. it
        points to the next byte after the unpacked value.

    Raises:
        :obj:`tlsmate.tls.ServerMalfunction`: If the buffer boundary is exceeded.
    """

    if offset >= len(data):
        raise tls.ServerMalfunction(tls.ServerIssue.PARAMETER_LENGTH_ERROR)

    return data[offset], offset + 1


def unpack_uint16(data: bytes, offset: int) -> Tuple[int, int]:
    """Unpacks a value from a given an buffer.

    Arguments:
        data: The buffer to unpack from.
        offset: The offset within the buffer.

    Returns:
        The tuple with the result. The first entry is the value that has been
        unpacked, the second one is the new offset in the buffer, i.e. it
        points to the next byte after the unpacked value.

    Raises:
        :obj:`tlsmate.tls.ServerMalfunction`: If the buffer boundary is exceeded.
    """

    if offset + 1 >= len(data):
        raise tls.ServerMalfunction(tls.ServerIssue.PARAMETER_LENGTH_ERROR)

    return struct.unpack("!H", data[offset : offset + 2])[0], offset + 2


def unpack_uint24(data: bytes, offset: int) -> Tuple[int, int]:
    """Unpacks a value from a given an buffer.

    Arguments:
        data: The buffer to unpack from.
        offset: The offset within the buffer.

    Returns:
        The tuple with the result. The first entry is the value that has been
        unpacked, the second one is the new offset in the buffer, i.e. it
        points to the next byte after the unpacked value.

    Raises:
        :obj:`tlsmate.tls.ServerMalfunction`: If the buffer boundary is exceeded.
    """

    if offset + 2 >= len(data):
        raise tls.ServerMalfunction(tls.ServerIssue.PARAMETER_LENGTH_ERROR)

    high_byte, val = struct.unpack("!BH", data[offset : offset + 3])
    return 0x10000 * high_byte + val, offset + 3


def unpack_uint32(data: bytes, offset: int) -> Tuple[int, int]:
    """Unpacks a value from a given an buffer.

    Arguments:
        data: The buffer to unpack from.
        offset: The offset within the buffer.

    Returns:
        The tuple with the result. The first entry is the value that has been
        unpacked, the second one is the new offset in the buffer, i.e. it
        points to the next byte after the unpacked value.

    Raises:
        :obj:`tlsmate.tls.ServerMalfunction`: If the buffer boundary is exceeded.
    """

    if offset + 3 >= len(data):
        raise tls.ServerMalfunction(tls.ServerIssue.PARAMETER_LENGTH_ERROR)

    return struct.unpack("!I", data[offset : offset + 4])[0], offset + 4


def unpack_bytes(data: bytes, offset: int, length: int) -> Tuple[bytes, int]:
    """Unpacks a given number of bytes from a given an buffer.

    Arguments:
        data: The buffer to unpack from.
        offset: The offset within the buffer.
        length: The number of bytes to unpack.

    Returns:
        The tuple with the result. The first entry is the value that has been
        unpacked, the second one is the new offset in the buffer, i.e. it
        points to the next byte after the unpacked value.

    Raises:
        :obj:`tlsmate.tls.ServerMalfunction`: If the buffer boundary is exceeded.
    """

    if offset + length > len(data):
        raise tls.ServerMalfunction(tls.ServerIssue.PARAMETER_LENGTH_ERROR)

    return data[offset : offset + length], offset + length


def dump(data: bytes, separator: str = " ", with_length: bool = True) -> str:
    """Provide a human readable representation of a bytes object.

    Arguments:
        data: The data to represent
        separator: the separator character(s) between the bytes. Defaults to " ".
        with_length: indication, if the length shall be appended in brackets.

    Returns:
        A human readable string, with a blank between each byte, and the length
        of the string appended in brackets.
    """

    ret = separator.join(f"{y:02x}" for y in data)
    if with_length:
        ret = ret + f" ({len(data)})"

    return ret


def dump_short(
    data: bytes,
    separator: str = " ",
    with_length: bool = True,
    start: int = 10,
    end: int = 10,
) -> str:
    """Like dump, but shorten the hexdump if it exceeds a certain limit.

        If the data is longer than start + end, then only a part of the data will
        be returned, and the middle of the data is collapsed to " ... ".

    Arguments:
        data: The data to represent
        separator: the separator character(s) between the bytes. Defaults to " ".
        with_length: indication, if the length shall be appended in brackets.
        start: the first number of bytes to display
        end: the last number of bytes to display.

    Returns:
        A human readable string, with a blank between each byte, and the length
        of the string appended in brackets.
    """

    length = len(data)
    if length <= start + end:
        return dump(data, separator, with_length)

    else:
        ret = (
            f"{dump(data[:start], separator=separator, with_length=False)} ... "
            f"{dump(data[-end:], separator=separator, with_length=False)}"
        )
        if with_length:
            ret += f" ({length})"

        return ret


def string(data: bytes) -> str:
    """Simple version of dump, separating the data with a colon, and omit the length

    Arguments:
        data (bytes): The data to represent

    Returns:
        str: A human readable string, with a colon between each byte.
    """

    return dump(data, separator=":", with_length=False)
