import io
import math
import struct

from whatap import PY2, PY3
from whatap.pack.pack import Pack

from whatap.value.null_value import NullValue

BYTE_MIN_VALUE = -128
BYTE_MAX_VALUE = 127
SHORT_MIN_VALUE = -32768
SHORT_MAX_VALUE = 32767
INT3_MIN_VALUE = -0x800000
INT3_MAX_VALUE = 0x007fffff
INT_MIN_VALUE = -0x80000000
INT_MAX_VALUE = 0x7fffffff
LONG5_MIN_VALUE = -0x8000000000
LONG5_MAX_VALUE = 0x0000007fffffffff
LONG_MIN_VALUE = -0x8000000000000000
LONG_MAX_VALUE = 0x7fffffffffffffff


class DataOutputX(object):
    def __init__(self, size=None):
        if size:
            self.buffer = io.BytesIO(bytearray(size))
        else:
            self.buffer = io.BytesIO()

    @staticmethod
    def toInt(buf, pos):
        ch1 = buf[pos] & 0xff
        ch2 = buf[pos + 1] & 0xff
        ch3 = buf[pos + 2] & 0xff
        ch4 = buf[pos + 3] & 0xff
        return ((ch1 << 24) + (ch2 << 16) + (ch3 << 8) + (ch4 << 0))

    def writePack(self, v, ln_fmt):
        self.writeShort(v.getPackType())
        v.write(self)
        if ln_fmt:
            remainder = len(self.buffer.getvalue()) % ln_fmt
            if remainder:
                self.write(bytearray(int(math.floor(ln_fmt - remainder))))
        return self

    def writeStep(self, step):
        self.writeByte(step.getStepType())
        step.write(self)
        return self

    @classmethod
    def toBytes(cls, v, ln_fmt=None):
        if isinstance(v, Pack):
            return cls().writePack(v, ln_fmt).toByteArray()

        buf = bytearray(4)
        buf[0] = ((v % 0x100000000) >> 24) & 0xff
        buf[1] = ((v % 0x100000000) >> 16) & 0xff
        buf[2] = ((v % 0x100000000) >> 8) & 0xff
        buf[3] = ((v % 0x100000000) >> 0) & 0xff
        return buf

    @classmethod
    def toBytesLong(cls, v):
        buf = bytearray(8)
        buf[0] = ((v % 0x100000000) >> 56) & 0xff
        buf[1] = ((v % 0x100000000) >> 48) & 0xff
        buf[2] = ((v % 0x100000000) >> 40) & 0xff
        buf[3] = ((v % 0x100000000) >> 32) & 0xff
        buf[4] = ((v % 0x100000000) >> 24) & 0xff
        buf[5] = ((v % 0x100000000) >> 16) & 0xff
        buf[6] = ((v % 0x100000000) >> 8) & 0xff
        buf[7] = ((v % 0x100000000) >> 0) & 0xff
        return buf

    def set(self, dest, pos, src):
        dest[pos:pos + len(src)] = src[0:]
        return dest

    def writeIntBytes(self, b):
        if not b or not len(b):
            self.writeInt(0)
        else:
            self.writeInt(len(b))
            self.write(b)
        return self

    def writeBoolean(self, v):
        self.buffer.write(struct.pack('>?', v))
        return self

    def writeByte(self, v):
        v = v & 0xFF
        self.buffer.write(struct.pack('>B', v))
        return self

    def writeShort(self, v):
        v = v & 0xFFFF
        self.buffer.write(struct.pack('>H', v))
        return self

    def writeInt3(self, v):
        v1 = (v >> 16) & 0xFF
        v2 = (v >> 8) & 0xFF
        v3 = (v >> 0) & 0xFF
        self.buffer.write(struct.pack('>BBB', v1, v2, v3))
        return self

    def writeInt(self, v):
        v = v & 0xFFFFFFFF
        self.buffer.write(struct.pack('>I', v))
        return self

    def writeLong5(self, v):
        v1 = ((v >> 32) & 0xFF)
        v2 = ((v >> 24) & 0xFF)
        v3 = ((v >> 16) & 0xFF)
        v4 = ((v >> 8) & 0xFF)
        v5 = ((v >> 0) & 0xFF)
        self.buffer.write(struct.pack('>BBBBB', v1, v2, v3, v4, v5))
        return self

    def writeLong(self, v):
        v = v & 0xFFFFFFFFFFFFFFFF
        self.buffer.write(struct.pack('>Q', v))
        return self

    def writeFloat(self, v):
        self.buffer.write(struct.pack('>f', v))
        return self

    def writeDouble(self, v):
        self.buffer.write(struct.pack('>d', v))
        return self

    def writeDecimal(self, v):
        if v == 0:
            self.writeByte(0)
        elif BYTE_MIN_VALUE <= v <= BYTE_MAX_VALUE:
            self.writeByte(1)
            self.writeByte(v)
        elif SHORT_MIN_VALUE <= v <= SHORT_MAX_VALUE:
            self.writeByte(2)
            self.writeShort(v)
        elif INT3_MIN_VALUE <= v <= INT3_MAX_VALUE:
            self.writeByte(3)
            self.writeInt3(v)
        elif INT_MIN_VALUE <= v <= INT_MAX_VALUE:
            self.writeByte(4)
            self.writeInt(v)
        elif LONG5_MIN_VALUE <= v <= LONG5_MAX_VALUE:
            self.writeByte(5)
            self.writeLong5(v)
        elif LONG_MIN_VALUE <= v <= LONG_MAX_VALUE:
            self.writeByte(8)
            self.writeLong(v)
        return self

    def write(self, v):
        self.buffer.write(v)
        return self

    def writeBlob(self, v):
        ln = len(v)
        if not v or not ln:
            self.writeByte(0)
        else:
            if ln <= 253:
                self.writeByte(ln)
                self.write(v)
            elif ln <= 65535:
                self.writeByte(255)
                self.writeShort(ln)
                self.write(v)
            else:
                self.writeByte(254)
                self.writeInt(ln)
                self.write(v)
        return self

    def writeText(self, v):
        if not v:
            self.writeByte(0)
        else:
            self.writeBlob(v.encode("utf-8"))
        return self

    def writeUTF(self, v):
        v = v.encode('utf-8')
        if len(v) > 65535:
            v = v[:65535]

        self.buffer.write(struct.pack('>H', len(v)))
        self.buffer.write(v)
        return self

    def writeValue(self, v):
        if not v:
            v = NullValue()

        self.writeByte(v.getValueType())
        v.write(self)
        return self

    def toByteArray(self):
        return self.buffer.getvalue()

    def flush(self):
        self.buffer.flush()

    def writeFloatArray(self, vv):
        if not vv:
            self.writeShort(0)
        else:
            self.writeShort(len(vv))
            for v in vv:
                self.writeFloat(v)
        return self

    def writeIntArray(self, vv):
        if not vv:
            self.writeShort(0)
        else:
            self.writeShort(len(vv))
            for v in vv:
                self.writeInt(v)
        return self

    def writeLongArray(self, vv):
        if not vv:
            self.writeShort(0)
        else:
            self.writeShort(len(vv))
            for v in vv:
                self.writeLong(v)
        return self

    def writeDecimalArray(self, vv):
        if not vv:
            self.writeShort(0)
        else:
            self.writeShort(len(vv))
            for v in vv:
                self.writeDecimal(v)
        return self

    def writeToPos(self, pos, v):
        if PY3:
            struct.pack_into('>I', self.buffer.getbuffer(), pos, v)
        else:
            b = io.BytesIO()
            b.write(struct.pack('>I', v & 0xFFFFFFFF))

            buffer_arr = bytearray(self.buffer.getvalue())
            buffer_arr[pos:pos + 4] = b.getvalue()
            self.buffer = io.BytesIO(buffer_arr)

    def size(self):
        return self.buffer.getbuffer().nbytes
        