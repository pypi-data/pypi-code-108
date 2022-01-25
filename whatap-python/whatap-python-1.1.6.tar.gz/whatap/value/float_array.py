from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum

from whatap.util.compare_util import CompareUtil


class FloatArray(Value):
    def __init__(self, value=None):
        super(FloatArray, self).__init__()
        self.value = value if isinstance(value, list) else []
        self._hash = 0

    def compareTo(self, object):
        if isinstance(object, FloatArray):
            return CompareUtil.compareTo(self.value, object.value)
        return 1

    def equals(self, object):
        if isinstance(object, FloatArray):
            return self.value == object.value
        return False

    def hashCode(self):
        if not self._hash:
            if not self.value:
                return 0

            result = 1
            for v in self.value:
                result = 31 * result + round(v)
            self._hash = result
        return self._hash

    def write(self, dout):
        dout.writeFloatArray(self.value)

    def read(self, din):
        self.value = din.readFloatArray()
        return self

    def getValueType(self):
        return ValueEnum.ARRAY_FLOAT
