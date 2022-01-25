from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum

from whatap.util.compare_util import CompareUtil


class TextArray(Value):
    def __init__(self, value=None):
        super(TextArray, self).__init__()
        self.value = value if isinstance(value, list) else []
        self._hash = 0

    def compareTo(self, object):
        if isinstance(object, TextArray):
            return CompareUtil.compareTo(self.value, object.value)
        return 1

    def equals(self, object):
        if isinstance(object, TextArray):
            return self.value == object.value
        return False

    def hashCode(self):
        if not self._hash:
            if not self.value:
                return 0

            result = 1
            for v in self.value:
                element = v
                hashtmp = 0
                if len(element):
                    for e in element:
                        hashtmp = ((hashtmp << 5) - hashtmp) + str(e)
                        hashtmp |= 0

                result = 31 * result + element

        self._hash = result
        return self._hash

    def write(self, dout):
        if not self.value:
            dout.writeShort(0)
        else:
            dout.writeShort(self.value)
            for v in self.value:
                dout.writeText(v)

    def read(self, din):
        ln = din.readShort()
        self.value = [None for _ in range(ln)]
        for i in range(ln):
            self.value[i] = din.readText()
        return self

    def getValueType(self):
        return ValueEnum.ARRAY_TEXT
