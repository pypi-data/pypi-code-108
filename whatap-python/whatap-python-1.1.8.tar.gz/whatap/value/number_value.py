from whatap.value.value import Value
from whatap.value.value_enum import ValueEnum


class NumberValue(Value):
    def __init__(self):
        super(NumberValue, self).__init__()

    def doubleValue(self):
        return self.value

    def floatValue(self):
        return self.value

    def intValue(self):
        return self.value

    def longValue(self):
        return self.value

    def add(self, num):
        if not num or not isinstance(num, NumberValue):
            return self

        if isinstance(num, ValueEnum.DECIMAL):
            self.value += num.longValue()
        elif isinstance(num, ValueEnum.FLOAT):
            self.value += num.floatValue()
        elif isinstance(num, ValueEnum.DOUBLE):
            self.value += num.doubleValue()
        else:
            from whatap.value.double_value import DoubleValue
            return DoubleValue(self.doubleValue() + num.doubleValue())
