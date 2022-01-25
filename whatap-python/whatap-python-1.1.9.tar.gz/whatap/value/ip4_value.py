from whatap.io.data_inputx import DataInputX
from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum

from whatap.util.compare_util import CompareUtil
from whatap.util.ip_util import IPUtil


class IP4Value(Value):
    def __init__(self, value=None):
        super(IP4Value, self).__init__()
        if isinstance(object, str):
            self.value = IPUtil.toBytes(value)
        else:
            self.value = None
        self.empty = bytearray(4)

    def compareTo(self, object):
        if isinstance(object, IP4Value):
            return CompareUtil.compareTo(self.value, object.value)
        return 1

    def equals(self, object):
        if isinstance(object, IP4Value):
            return self.value == object.value
        return False

    def hashCode(self):
        if self.value == self.empty:
            return 0
        return DataInputX.toInt(self.value, 0)

    def write(self, dout):
        if not self.value:
            self.value = self.empty
        dout.write(self.value)

    def read(self, din):
        if not self.value:
            self.value = self.empty
        self.value = din.read(4)
        return self

    def toString(self):
        if not self.value:
            self.value = self.empty
        return IPUtil.toString(self.value)

    def getValueType(self):
        return ValueEnum.IP4ADDR
