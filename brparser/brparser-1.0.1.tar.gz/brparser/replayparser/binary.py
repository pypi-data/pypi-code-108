from struct import unpack_from, calcsize

class Binary:

    def __init__(self, data):
        self.offset = 0
        self.data = data

    def read(self, format):
        data = unpack_from(format, self.data, self.offset)
        self.offset += calcsize(format)
        return data

    def readByte(self):
        return self.read("<b")[0]

    def readBool(self):
        return self.read("<?")[0]

    def readInt(self):
        return self.read("<i")[0]

    def readShort(self):
        return self.read("<h")[0]

    def readLong(self):
        return self.read("<q")[0]

    def readString(self):
        if self.data[self.offset] == 0x00:
            self.offset += 1
        elif self.data[self.offset] == 0x0b:
            self.offset += 1
            length = self._uleb128decode()
            start = self.offset
            self.offset += length
            return self.data[start:self.offset].decode("utf-8-sig")
        else:
            raise ValueError("Invalid string: first byte should be 0x00 or "
                f"0x0b, but got 0x{replay_data[self.offset]:02x}")

    def _uleb128decode(self):
        shift = 0
        value = 0
        while True:
            byte = self.data[self.offset]
            value |= (byte & 0b01111111) << shift
            self.offset += 1
            if (byte & 0b10000000) == 0x00:
                break
            shift += 7
        return value
