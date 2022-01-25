import math

from whatap.io.data_outputx import DataOutputX
from whatap.util.cardinality.murmurhash import MurMurHash
from whatap.util.cardinality.registerset import RegisterSet


def getAlphaMM(p, m):
    if p == 4:
        return 0.673 * m * m
    elif p == 5:
        return 0.697 * m * m
    elif p == 6:
        return 0.709 * m * m
    else:
        return (0.7213 / (1 + 1.079 / m)) * m * m


def linearCounting(m, V):
    return m * math.log(m / V)


def numberOfLeadingZeros(i):
    if not i:
        return 32

    n = 1
    if (i % 0x100000000) >> 16 == 0:
        n += 16
        i <<= 16
    if (i % 0x100000000) >> 24 == 0:
        n += 8
        i <<= 8
    if (i % 0x100000000) >> 28 == 0:
        n += 4
        i <<= 4
    if (i % 0x100000000) >> 30 == 0:
        n += 2
        i <<= 2

    n -= (i % 0x100000000) >> 31
    return n


class HyperLogLog(object):
    def __init__(self):
        self.log2m = 10
        self.registerSet = RegisterSet(1 << self.log2m)
        m = 1 << self.log2m
        self.alphaMM = getAlphaMM(self.log2m, m)

    def offerHashed(self, hashedValue):
        j = (hashedValue % 0x100000000) >> (32 - self.log2m)
        r = numberOfLeadingZeros(
            (hashedValue << self.log2m) | (1 << (self.log2m - 1)) + 1) + 1
        return self.registerSet.updateIfGreater(j, r)

    def offer(self, o):
        x = MurMurHash.hash(o)
        return self.offerHashed(x)

    def cardinality(self):
        registerSum = 0
        count = self.registerSet.count
        zeros = 0.0
        for j, _ in enumerate(count):
            val = self.registerSet.get(j)
            registerSum += 1.0 / (1 << val)
            if int(val) == 0:
                zeros += 1

        estimate = self.alphaMM * (1 / registerSum)
        if estimate <= (5.0 / 2.0) * count:
            return math.round(linearCounting(count, zeros))
        else:
            return math.round(estimate)

    def getBytes(self):
        dout = DataOutputX()
        dout.writeInt(self.log2m)
        dout.writeInt(self.registerSet.size)
        for m in self.registerSet.readOnlyBits():
            dout.writeInt(m)
        return dout.toByteArray()
