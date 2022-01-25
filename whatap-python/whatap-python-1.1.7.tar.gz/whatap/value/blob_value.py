from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum

from whatap.util.compare_util import CompareUtil
from whatap.util.hash_util import HashUtil


class BlobValue(Value):
    def __init__(self, value=None):
        super(BlobValue, self).__init__()
        self.value = value

    def compareTo(self, object):
        if isinstance(object, BlobValue):
            return CompareUtil.compareTo(self.value, object.value)
        return 1

    def equals(self, object):
        if isinstance(object, BlobValue):
            if not self.value:
                return object.value is None
            return self.value == object.value
        return False

    def hashCode(self):
        if not self.value:
            return 0
        return HashUtil.hash(self.value)

    def write(self, dout):
        dout.writeBlob(self.value)

    def read(self, din):
        self.value = din.readBlob()
        return self

    def getValueType(self):
        return ValueEnum.BLOB
