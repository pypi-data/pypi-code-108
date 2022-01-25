from whatap.value.number_value import NumberValue
from whatap.value.value_enum import ValueEnum

from whatap.util.compare_util import CompareUtil


class FloatValue(NumberValue):
    def __init__(self, value=0.0):

        super(FloatValue, self).__init__()
        self.value = value

    def compareTo(self, object):
        if isinstance(object, FloatValue):
            return CompareUtil.compareTo(self.value, object.value)
        return 1

    def equals(self, object):
        if isinstance(object, FloatValue):
            return self.value == object.value
        return False

    def hashCode(self):
        return round(self.value)

    def write(self, dout):
        dout.writeFloat(self.value)

    def read(self, din):
        self.value = din.readFloat()
        return self

    def getValueType(self):
        return ValueEnum.FLOAT
