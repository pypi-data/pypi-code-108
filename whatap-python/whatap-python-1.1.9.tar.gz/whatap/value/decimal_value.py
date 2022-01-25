from whatap.value.number_value import NumberValue
from whatap.value.value_enum import ValueEnum


class DecimalValue(NumberValue):
    def __init__(self, value=None):
        super(DecimalValue, self).__init__()
        self.value = value

    def compareTo(self, object):
        if isinstance(object, DecimalValue):
            if self.value < object.value:
                return -1
            elif self.value == object.value:
                return 0
            else:
                return 1
        return 1

    def equals(self, object):
        if isinstance(object, DecimalValue):
            return self.value == object.value
        return False

    def hashCode(self):
        return self.value ^ (self.value >> 32)

    def write(self, dout):
        dout.writeDecimal(self.value)

    def read(self, din):
        self.value = din.readDecimal()
        return self

    def getValueType(self):
        return ValueEnum.DECIMAL
