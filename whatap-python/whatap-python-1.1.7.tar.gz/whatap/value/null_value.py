from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum


class NullValue(Value):
    def __init__(self):
        super(NullValue, self).__init__()

    def compareTo(self, object):
        if isinstance(object, NullValue):
            return 0
        return 1

    def equals(self, object):
        return isinstance(object, NullValue)

    def hashCode(self):
        return 0

    def getValueType(self):
        return ValueEnum.NULL
