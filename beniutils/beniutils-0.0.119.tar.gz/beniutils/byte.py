import struct
from typing import Any

import chardet

from beniutils import getLimitedValue


def decode(value: bytes):
    data = chardet.detect(value)
    encoding = data["encoding"] or "utf8"
    return value.decode(encoding)


class BytesWriter():

    def __init__(self, isBigEndian: bool = True):

        self.isBigEndian = isBigEndian
        self.formatAry: list[str] = []
        self.valueAry: list[Any] = []

    def toBytes(self):
        formatStr = self.isBigEndian and ">" or "<"
        formatStr += "".join(self.formatAry)
        return struct.pack(formatStr, *self.valueAry)

    def _write(self, format: str, value: int | float | bool | str | bytes):
        self.formatAry.append(format)
        self.valueAry.append(value)

    def _writeAry(self, func: Any, ary: list[Any]):
        self.writeUInt(len(ary))
        for value in ary:
            func(value)
        return self

    # -----

    def writeShort(self, value: int):
        self._write("h", getLimitedValue(value, -32768, 32767))             # int16
        return self

    def writeUShort(self, value: int):
        self._write("H", getLimitedValue(value, 0, 65535))  # int16
        return self

    def writeInt(self, value: int):
        self._write("i", getLimitedValue(value, -2147483648, 2147483647))  # int32
        return self

    def writeUInt(self, value: int):
        self._write("I", getLimitedValue(value, 0, 4294967295))  # int32
        return self

    def writeLong(self, value: int):
        self._write("q", getLimitedValue(value, -9223372036854775808, 9223372036854775807))  # int64
        return self

    def writeULong(self, value: int):
        self._write("Q", getLimitedValue(value, 0, 18446744073709551615))  # int64
        return self

    def writeFloat(self, value: float):
        self._write("f", value)
        return self

    def writeDouble(self, value: float):
        self._write("d", value)
        return self

    def writeBool(self, value: bool):
        self._write("?", value)
        return self

    def writeStr(self, value: str):
        valueBytes = value.encode("utf8")
        self._write("H", len(value)) # 0 ~ 65535
        self._write(f"{len(valueBytes)}s", valueBytes)
        # self._write(f"{len(valueBytes)+1}p", valueBytes) # 一些小语种在C#解析会出问题，例如俄语，印地语，但是没有找到绝对的规律
        return self

    # -----

    def writeShortAry(self, ary: list[int]):
        return self._writeAry(self.writeShort, ary)

    def writeUShortAry(self, ary: list[int]):
        return self._writeAry(self.writeUShort, ary)

    def writeIntAry(self, ary: list[int]):
        return self._writeAry(self.writeInt, ary)

    def writeUIntAry(self, ary: list[int]):
        return self._writeAry(self.writeUInt, ary)

    def writeLongAry(self, ary: list[int]):
        return self._writeAry(self.writeLong, ary)

    def writeULongAry(self, ary: list[int]):
        return self._writeAry(self.writeULong, ary)

    def writeFloatAry(self, ary: list[float]):
        return self._writeAry(self.writeFloat, ary)

    def writeDoubleAry(self, ary: list[float]):
        return self._writeAry(self.writeDouble, ary)

    def writeBoolAry(self, ary: list[bool]):
        return self._writeAry(self.writeBool, ary)

    def writeStrAry(self, ary: list[str]):
        return self._writeAry(self.writeStr, ary)
