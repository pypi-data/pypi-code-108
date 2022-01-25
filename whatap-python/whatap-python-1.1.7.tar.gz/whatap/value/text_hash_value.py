from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum

from whatap.util.hash_util import HashUtil


class TextHashValue(Value):
    def __init__(self, value=None):
        super(TextHashValue, self).__init__()
        self.value = HashUtil.crc32(value)

    def compareTo(self, object):
        if isinstance(object, TextHashValue):
            if self.value < object.value:
                return -1
            elif self.value == object.value:
                return 0
            return 1
        return 1

    def equals(self, object):
        if isinstance(object, TextHashValue):
            return self.value == object.value
        return False

    def hashCode(self):
        return self.value

    def write(self, dout):
        dout.writeInt(self.value)

    def read(self, din):
        self.value = din.readInt()
        return self

    def getValueType(self):
        return ValueEnum.TEXT_HASH
