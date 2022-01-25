from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum


class BooleanValue(Value):
    def __init__(self, value=None):
        super(BooleanValue, self).__init__()
        self.value = value if isinstance(value, bool) else False

    def compareTo(self, object):
        if isinstance(object, BooleanValue):
            if self.value == object.value:
                return 0
            return 1 if self.value else -1
        return 1

    def equals(self, object):
        if isinstance(object, BooleanValue):
            return self.value == object.value
        return False

    def hashCode(self):
        return 1 if self.value else 0

    def write(self, dout):
        dout.writeBoolean(self.value)

    def read(self, din):
        self.value = din.readBoolean()
        return self

    def getValueType(self):
        return ValueEnum.BOOLEAN
