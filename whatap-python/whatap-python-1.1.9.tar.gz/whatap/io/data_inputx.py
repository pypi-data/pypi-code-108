import io
import struct
from whatap.pack.pack_enum import PackEnum

from whatap.value.value_enum import ValueEnum


class DataInputX(object):
    def __init__(self, v):
        self.buffer = io.BytesIO(v)

    @staticmethod
    def toInt(buf, pos):
        ch1 = buf[pos] & 0xff
        ch2 = buf[pos + 1] & 0xff
        ch3 = buf[pos + 2] & 0xff
        ch4 = buf[pos + 3] & 0xff
        return ((ch1 << 24) + (ch2 << 16) + (ch3 << 8) + (ch4 << 0))

    def readPack(self):
        type = self.readShort()
        return PackEnum.create(type).read(self)

    def readValue(self):
        type = self.readByte()
        return ValueEnum.create(type).read(self)

    # TODO
    # def available(self):
    #     return len(self.buffer.getvalue())- self.offset > 0

    # TODO
    # def readStep(self):
    #     raise
    #     # byte type = this.inner.readByte();
    #     # return StepEnum.create(type).read(this);
    #     return None

    def readIntBytes(self, max):
        ln = self.readInt()
        if ln < 0 or ln > max:
            raise Exception('error')
        return self.buffer.read(ln)

    def readBoolean(self):
        v = self.buffer.read(1)
        return struct.unpack('>?', v)[0]

    def readByte(self):
        v = self.buffer.read(1)
        return struct.unpack('>b', v)[0]

    def readShort(self):
        v = self.buffer.read(2)
        return struct.unpack('>h', v)[0]

    def readInt3(self):
        s = self.buffer.read(3)
        chrs = struct.unpack('>bBB', s)
        ch1 = (chrs[0])
        ch2 = (chrs[1])
        ch3 = (chrs[2])
        return (ch1 << 16) + (ch2 << 8) + ch3

    def readInt(self):
        v = self.buffer.read(4)

        return struct.unpack('>i', v)[0]

    def readLong5(self):
        s = self.buffer.read(5)
        chrs = struct.unpack('>bBBBB', s)
        ch1 = (chrs[0])
        ch2 = (chrs[1])
        ch3 = (chrs[2])
        ch4 = (chrs[3])
        ch5 = (chrs[4])
        return ((ch1 << 32) + (ch2 << 24) + (ch3 << 16) + (ch4 << 8) + (ch5))

    def readLong(self):
        v = self.buffer.read(8)
        return struct.unpack('>q', v)[0]

    def readFloat(self):
        v = self.buffer.read(4)
        return struct.unpack('>f', v)[0]

    def readDouble(self):
        v = self.buffer.read(8)
        return struct.unpack('>d', v)[0]

    def readDecimal(self):
        ln = self.readByte()
        if ln == 0:
            return 0
        elif ln == 1:
            return self.readByte()
        elif ln == 2:
            return self.readShort()
        elif ln == 3:
            return self.readInt3()
        elif ln == 4:
            return self.readInt()
        elif ln == 5:
            return self.readLong5()
        else:
            return self.readLong()

    def read(self, ln):
        return self.buffer.read(ln)

    def readBlob(self):
        baselen = self.readByte() & 0xff
        if baselen == 255:
            ln = self.readShort() & 0xffff
            return self.buffer.read(ln)
        elif baselen == 254:
            ln = self.readInt()
            return self.buffer.read(ln)
        elif baselen == 0:
            return []
        else:
            return self.buffer.read(baselen)

    def readText(self):
        arr = self.readBlob()
        if not len(arr):
            return ''
        else:
            return arr.decode("utf-8")

    def toByteArray(self):
        return self.buffer.getvalue()

    def readFloatArray(self):
        ln = self.readShort()
        data = []
        for _ in range(ln):
            data.append(self.readFloat())
        return data

    def readIntArray(self):
        ln = self.readShort()
        data = []
        for _ in range(ln):
            data.append(self.readInt())
        return data

    def readLongArray(self):
        ln = self.readShort()
        data = []
        for _ in range(ln):
            data.append(self.readLong())
        return data

    def readDecimalArray(self):
        ln = self.readShort()
        data = []
        for _ in range(ln):
            data.append(self.readDecimal())
        return data
