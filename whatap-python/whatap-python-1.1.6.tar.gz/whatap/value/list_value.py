from whatap.value.boolean_value import BooleanValue
from whatap.value.decimal_value import DecimalValue
from whatap.value.double_value import DoubleValue
from whatap.value.float_value import FloatValue
from whatap.value.number_value import NumberValue
from whatap.value.text_value import TextValue

from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum


class ListValue(Value):
    def __init__(self, valueList=None):
        super(ListValue, self).__init__()
        self.valueList = valueList if isinstance(valueList, list) else []

    def getBoolean(self, i):
        v = self.valueList[i]
        if isinstance(v, BooleanValue):
            return v.value
        return False

    def getDouble(self, i):
        v = self.valueList[i]
        if isinstance(v, NumberValue):
            return v.doubleValue()
        return 0.0

    def getLong(self, i):
        v = self.valueList[i]
        if isinstance(v, NumberValue):
            return v.longValue()
        return 0

    def getInt(self, i):
        v = self.valueList[i]
        if isinstance(v, NumberValue):
            return v.intValue()
        return 0

    def getString(self, i):
        v = self.valueList[i]
        if isinstance(v, TextValue):
            return v.value
        if not v:
            return None
        return v

    def set(self, i, value):
        self.valueList[i] = value

    def addValue(self, value):
        self.valueList.append(value)
        return self

    def addBoolean(self, value):
        self.valueList.append(BooleanValue(value))
        return self

    def addDouble(self, value):
        self.valueList.append(DoubleValue(value))
        return self

    def addLong(self, value):
        self.valueList.append(DecimalValue(value))
        return self

    def addFloat(self, value):
        self.valueList.append(FloatValue(value))
        return self

    def addString(self, value):
        self.valueList.append(TextValue(value))
        return self

    def addStringArray(self, value):
        if isinstance(value, list):
            for v in value:
                self.addString(v)
        return self

    def addValueArray(self, value):
        if isinstance(value, list):
            for v in value:
                self.addValue(v)
        return self

    def size(self):
        return len(self.valueList)

    def write(self, dout):
        size = self.size()
        dout.writeDecimal(size)
        for i in range(size):
            dout.writeValue(self.valueList[i])

    def read(self, din):
        for _ in range(din.readDecimal()):
            self.addValue(din.readValue())

    def getValueType(self):
        return ValueEnum.LIST

    def toObject(self):
        return self.valueList
