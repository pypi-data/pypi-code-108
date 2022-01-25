from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum

from whatap.util.compare_util import CompareUtil


class TextValue(Value):
    def __init__(self, value=None):
        super(TextValue, self).__init__()
        self.value = str('' if not value else value)
    
    def compareTo(self, object):
        if isinstance(object, TextValue):
            return CompareUtil.compareTo(self.value, object.value)
        return 1
    
    def equals(self, object):
        if isinstance(object, TextValue):
            if self.value is None:
                return object.value is None
            return self.value == object.value
        return False
    
    def hashCode(self):
        if not self.value:
            return 0
            return 0
        
        hash = 0
        if not hash and len(self.value):
            for v in self.value:
                hash = 31 * hash + v
        return hash
    
    def write(self, dout):
        dout.writeText(self.value)
    
    def read(self, din):
        self.value = din.readText()
        return self
    
    def getValueType(self):
        return ValueEnum.TEXT
