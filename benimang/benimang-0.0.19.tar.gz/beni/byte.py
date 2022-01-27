import struct
from typing import Any, Final, Literal, cast

import chardet

from beni import getvalue_inside


def decode(value: bytes):
    data = chardet.detect(value)
    encoding = data['encoding'] or 'utf8'
    return value.decode(encoding)


EndianType: Final = Literal[
    # https://docs.python.org/zh-cn/3/library/struct.html#byte-order-size-and-alignment
    '@',  # 按原字节
    '=',  # 按原字节
    '<',  # 小端
    '>',  # 大端
    '!',  # 网络（=大端）
]


class BytesWriter():

    def __init__(self, endian: EndianType):
        self.endian = endian
        self.formatAry: list[str] = []
        self.valueAry: list[Any] = []

    def to_bytes(self):
        return struct.pack(
            f'{self.endian}{"".join(self.formatAry)}',
            *self.valueAry
        )

    def _write(self, format: str, value: int | float | bool | str | bytes):
        self.formatAry.append(format)
        self.valueAry.append(value)

    def _write_list(self, func: Any, ary: list[Any]):
        self.write_uint(len(ary))
        for value in ary:
            func(value)
        return self

    # ---------------------------------------------------------------------------

    def write_short(self, value: int):
        self._write('h', getvalue_inside(value, -32768, 32767))  # int16
        return self

    def write_ushort(self, value: int):
        self._write('H', getvalue_inside(value, 0, 65535))  # int16
        return self

    def write_int(self, value: int):
        self._write('i', getvalue_inside(value, -2147483648, 2147483647))  # int32
        return self

    def write_uint(self, value: int):
        self._write('I', getvalue_inside(value, 0, 4294967295))  # int32
        return self

    def write_long(self, value: int):
        self._write('q', getvalue_inside(value, -9223372036854775808, 9223372036854775807))  # int64
        return self

    def write_ulong(self, value: int):
        self._write('Q', getvalue_inside(value, 0, 18446744073709551615))  # int64
        return self

    def write_float(self, value: float):
        self._write('f', value)
        return self

    def write_double(self, value: float):
        self._write('d', value)
        return self

    def write_bool(self, value: bool):
        self._write('?', value)
        return self

    def write_str(self, value: str):
        valueBytes = value.encode('utf8')
        count = len(valueBytes)
        self.write_ushort(count)
        self._write(f'{count}s', valueBytes)
        return self

    # ---------------------------------------------------------------------------

    def writelist_short(self, ary: list[int]):
        return self._write_list(self.write_short, ary)

    def writelist_ushort(self, ary: list[int]):
        return self._write_list(self.write_ushort, ary)

    def writelist_int(self, ary: list[int]):
        return self._write_list(self.write_int, ary)

    def writelist_uint(self, ary: list[int]):
        return self._write_list(self.write_uint, ary)

    def writelist_long(self, ary: list[int]):
        return self._write_list(self.write_long, ary)

    def writelist_ulong(self, ary: list[int]):
        return self._write_list(self.write_ulong, ary)

    def writelist_float(self, ary: list[float]):
        return self._write_list(self.write_float, ary)

    def writelist_double(self, ary: list[float]):
        return self._write_list(self.write_double, ary)

    def writelist_bool(self, ary: list[bool]):
        return self._write_list(self.write_bool, ary)

    def writelist_str(self, ary: list[str]):
        return self._write_list(self.write_str, ary)


class BytesReader():

    offset: int
    data: bytes

    def __init__(self, endian: EndianType, data: bytes):
        self.endian = endian
        self.offset = 0
        self.data = data

    def _read(self, fmt: str):
        result = struct.unpack_from(fmt, self.data, self.offset)[0]
        self.offset += struct.calcsize(fmt)
        return result

    def _readList(self, func: Any):
        ary: list[Any] = []
        count = self.read_uint()
        for _ in range(count):
            ary.append(func())
        return ary

    # ---------------------------------------------------------------------------

    def read_short(self):
        return cast(int, self._read('h'))  # int16

    def read_ushort(self):
        return cast(int, self._read('H'))  # int16

    def read_int(self):
        return cast(int, self._read('i'))  # int32

    def read_uint(self):
        return cast(int, self._read('I'))  # int32

    def read_long(self):
        return cast(int, self._read('q'))  # int64

    def read_ulong(self):
        return cast(int, self._read('Q'))  # int64

    def read_float(self):
        return cast(float, self._read('f'))

    def read_double(self):
        return cast(float, self._read('d'))

    def read_bool(self):
        return cast(bool, self._read('?'))

    def read_str(self):
        count = self.read_ushort()
        return cast(str, self._read(f'{count}s').decode())

    # ---------------------------------------------------------------------------

    def readlist_short(self):
        return cast(list[int], self._readList(self.read_short))

    def readlist_ushort(self):
        return cast(list[int], self._readList(self.read_ushort))

    def readlist_int(self):
        return cast(list[int], self._readList(self.read_int))

    def readlist_uint(self):
        return cast(list[int], self._readList(self.read_uint))

    def readlist_long(self):
        return cast(list[int], self._readList(self.read_long))

    def readlist_ulong(self):
        return cast(list[int], self._readList(self.read_ulong))

    def readlist_float(self):
        return cast(list[float], self._readList(self.read_float))

    def readlist_double(self):
        return cast(list[float], self._readList(self.read_double))

    def readlist_bool(self):
        return cast(list[bool], self._readList(self.read_bool))

    def readlist_str(self):
        return cast(list[str], self._readList(self.read_str))
