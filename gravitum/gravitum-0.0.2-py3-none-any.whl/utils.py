from functools import reduce
from operator import add
from typing import List, Union

import numpy as np

from .types import int8, int16, int32, int64, \
    uint8, uint16, uint32, uint64, \
    IntTypes, IntMeta


def get_size(value_or_type: Union[type, IntTypes]) -> int:
    """Get size (bytes) of the type or the value."""
    data_type = value_or_type \
        if type(value_or_type) == IntMeta \
        else type(value_or_type)
    if data_type in [int8, uint8]:
        return 1
    elif data_type in [int16, uint16]:
        return 2
    elif data_type in [int32, uint32]:
        return 4
    elif data_type in [int64, uint64]:
        return 8
    raise NotImplementedError()


def get_signed(value_or_type: Union[type, IntTypes]) -> bool:
    """Get is signed of the type or the value."""
    data_type = value_or_type \
        if type(value_or_type) == IntMeta \
        else type(value_or_type)
    return issubclass(data_type, np.signedinteger)


def get_type(size: int, signed: bool) -> type:
    """Get int type by size and signed.

    :param size: The size (bytes) of the type.
    :param signed: Is the type signed.
    """
    if size == 1:
        return int8 if signed else uint8
    elif size == 2:
        return int16 if signed else uint16
    elif size == 4:
        return int32 if signed else uint32
    elif size == 8:
        return int64 if signed else uint64
    raise NotImplementedError()


def int_to_bytes(
        value: Union[int, IntTypes],
        data_type: type = None,
        byteorder: str = 'little'
) -> bytes:
    """Covert a value of int type to bytes.

    Support value of basic int type and numpy int type.

    If the type of value is basic int, you should specified parameter
    `data_type`.

    :param value: The value to convert to bytes.
    :param data_type: The type of the value.
    :param byteorder: The byte order of the value.
    """
    data_type = data_type or type(value)
    return int(data_type(value)).to_bytes(
        length=get_size(data_type),
        byteorder=byteorder,
        signed=get_signed(data_type)
    )


def int_from_bytes(
        data: bytes,
        data_type: type,
        byteorder: str = 'little'
) -> IntTypes:
    """Covert bytes to a value of int type.

    :param data: The source bytes to convert to int value.
    :param data_type: The type of the value.
    :param byteorder: The byte order of the data.
    """
    return data_type(int.from_bytes(
        data,
        byteorder=byteorder,
        signed=get_signed(data_type)
    ))


def values2bytearray(
        values: List[Union[int, IntTypes]],
        nbits: int = 32,
        byteorder: str = 'little',
        signed: bool = False,
) -> bytearray:
    """Covert a list to a bytearray.

    Support list of basic int type and numpy int type.

    If the type of value in the list is basic int, you should specified
    parameter `nbits`, otherwise it will use the default value 32. If
    the type of value in the list is numpy int, the data size will base
    on the actual size of the type.

    :param values: The source list.
    :param nbits: The data size (bits).
    :param byteorder: The byte order of the value.
    :param signed: Is the value signed.
    """
    if values:
        size = nbits // 8 \
            if isinstance(values[0], int) \
            else get_size(type(values[0]))
        signed = signed \
            if isinstance(values[0], int) \
            else get_signed(type(values[0]))
    else:
        size = nbits // 8

    data_type = get_type(size, signed)
    data_list = [int_to_bytes(
        value,
        data_type=data_type,
        byteorder=byteorder
    ) for value in values]

    return bytearray(reduce(add, data_list))


def bytearray2values(
        source: bytearray,
        nbits: int = 32,
        byteorder: str = 'little',
        signed: bool = False,
) -> List[Union[IntTypes]]:
    """Convert a bytearray to a list.

    :param source: The source bytearray.
    :param nbits: The data size (bits).
    :param byteorder: The byte order of the value.
    :param signed: Is the value signed.
    """
    size = nbits // 8
    data_type = get_type(size=size, signed=signed)

    data_list = [
        bytes(source[i * size:(i + 1) * size])
        for i in range(len(source) // size)
    ]

    return [int_from_bytes(
        data,
        data_type=data_type,
        byteorder=byteorder
    ) for data in data_list]


def offset_n(x: IntTypes, n: int, t: type, byteorder: str) -> IntTypes:
    """Get the nth member of the value.

    :param x: The value of int type.
    :param n: Nth member of the value.
    :param t: The type of member in the value.
    :param byteorder: The byte order of the value.
    """
    size = get_size(t)
    data = int_to_bytes(x, byteorder=byteorder)
    return int_from_bytes(
        data[n * size: (n + 1) * size],
        data_type=t,
        byteorder=byteorder
    )


def b_swap(
        value: Union[int, IntTypes],
        nbits: int = 32,
        byteorder: str = 'little',
        signed: bool = False,
) -> Union[int, IntTypes]:
    """Swap bytes on the value.

    :param value: The source value.
    :param nbits: The data size (bits).
    :param byteorder: The byte order of the value.
    :param signed: Is the value signed.
    """
    size = nbits // 8 \
        if isinstance(value, int) \
        else get_size(type(value))
    signed = signed \
        if isinstance(value, int) \
        else get_signed(type(value))

    data_type = get_type(size, signed)
    data = int_to_bytes(value, data_type=data_type, byteorder=byteorder)

    return int_from_bytes(data[::-1], data_type=data_type, byteorder=byteorder)
