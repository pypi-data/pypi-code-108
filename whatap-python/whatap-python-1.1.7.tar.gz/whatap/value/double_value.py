from whatap.value.number_value import NumberValue
from whatap.value.value_enum import ValueEnum


class DoubleValue(NumberValue):
    def __init__(self, value=None):
        super(DoubleValue, self).__init__()
        self.value = value

    def compareTo(self, object):
        if isinstance(object, DoubleValue):
            if self.value != object.value:
                return 1 if self.value > object.value else -1
            return 0
        return 1

    def equals(self, object):
        if isinstance(object, DoubleValue):
            return self.value == object.value
        return False

    def hashCode(self):
        return self.value ^ (self.value >> 32)

    def write(self, dout):
        dout.writeDouble(self.value)

    def read(self, din):
        self.value = din.readDouble()
        return self

    def getValueType(self):
        return ValueEnum.DOUBLE
