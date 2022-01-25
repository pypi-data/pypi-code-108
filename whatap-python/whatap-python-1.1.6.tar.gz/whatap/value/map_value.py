from whatap.value.boolean_value import BooleanValue
from whatap.value.decimal_value import DecimalValue
from whatap.value.number_value import NumberValue
from whatap.value.text_value import TextValue
from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum

from whatap.value.list_value import ListValue


class MapValue(Value):
    def __init__(self):
        super(MapValue, self).__init__()
        self.table = {} #OrderedDict()

    def equals(self, obj):
        if self == obj:
            return True
        elif not obj:
            return False

        elif not self.table:
            if obj.table:
                return False
        elif self.table != obj.table:
            return False
        return True

    def size(self):
        return len(self.table)

    def isEmpty(self):
        return self.size() == 0

    def containsKey(self, key):
        return self.get(key) is not None

    def keys(self):
        return self.table.keys()

    def get(self, key):
        return self.table.get(key)

    def getBoolean(self, key):
        v = self.get(key)
        if isinstance(v, BooleanValue):
            return v.value
        return False

    def getInt(self, key):
        v = self.get(key)
        if isinstance(v, NumberValue):
            return v.intValue()
        return 0

    def getLong(self, key):
        v = self.get(key)
        if isinstance(v, NumberValue):
            return v.longValue()
        return 0

    def getFloat(self, key):
        v = self.get(key)
        if isinstance(v, NumberValue):
            return v.floatValue()
        return 0

    def getText(self, key):
        v = self.get(key)
        if isinstance(v, TextValue):
            return v.value
        return None

    def put(self, key, value):
        self.table[key] = value
        return self

    def putValue(self, key, value):
        self.table[key] = value
        return self

    def putString(self, key, value):
        self.table[key] = TextValue(value)
        return self

    def putLong(self, key, value):
        self.table[key] = DecimalValue(value)

    def remove(self, key):
        val = self.table[key]
        del self.table[key]
        return val

    def clear(self):
        self.table = {}

    def getValueType(self):
        return ValueEnum.MAP

    def write(self, dout):
        dout.writeDecimal(self.size())
        for key in self.table.keys():
            dout.writeText(key)
            dout.writeValue(self.get(key))

    def read(self, din):
        count = din.readDecimal()
        for _ in range(count):
            key = din.readText()
            value = din.readValue()
            self.putValue(key, value)
        return self

    def newList(self, name):
        list = ListValue()
        self.putValue(name, list)
        return list

    def getList(self, key):
        return self.get(key)

    def toObject(self):
        return self.table

    def putAllMap(self, m):
        for key in self.table.keys():
            value = m.get(key)
            if isinstance(value, Value):
                self.table[key] = value

    def putAllMapValue(self, m):
        self.putAllMap(m.table)
