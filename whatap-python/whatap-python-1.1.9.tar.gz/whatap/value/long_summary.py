from whatap.value.summary_value import SummaryValue
from whatap.value.value_enum import ValueEnum


class LongSummary(SummaryValue):
    def __init__(self):
        super(LongSummary, self).__init__()
        self.sum = 0
        self.count = 0
        self.min = 0
        self.max = 0

    def getValueType(self):
        return ValueEnum.LONG_SUMMARY

    def write(self, dout):
        dout.writeLong(self.sum)
        dout.writeInt(self.count)
        dout.writeLong(self.min)
        dout.writeLong(self.max)

    def read(self, din):
        self.sum = din.readLong()
        self.count = din.readInt()
        self.min = din.readLong()
        self.max = din.readLong()
        return self

    def addCount(self):
        self.count += 1

    def add(self, value):
        if not value:
            return self

        if isinstance(value, int):
            if not self.count:
                self.sum = value
                self.count = 1
                self.max = value
                self.min = value
            else:
                self.sum += value
                self.count += 1
                self.max = max(self.max, value)
                self.min = min(self.min, value)

        elif isinstance(value, SummaryValue):
            if not value.getCount():
                return self

            self.count += value.getCount()
            self.sum += value.doubleSum()
            self.min = min(self.min, value.doubleMin())
            self.max = max(self.max, value.doubleMax())
        return self

    def longSum(self):
        return self.sum

    def longMin(self):
        return self.min

    def longMax(self):
        return self.max

    def longAvg(self):
        return 0 if not self.count else self.sum / self.count

    def doubleSum(self):
        return self.sum

    def doubleMin(self):
        return self.min

    def doubleMax(self):
        return self.max

    def doubleAvg(self):
        return 0 if not self.count else self.sum / self.count

    def getCount(self):
        return self.count
