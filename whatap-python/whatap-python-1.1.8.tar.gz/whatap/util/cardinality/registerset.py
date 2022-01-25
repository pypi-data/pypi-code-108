LOG2_BITS_PER_WORD = 6
REGISTER_SIZE = 5


def getBits(count):
    return int(count / LOG2_BITS_PER_WORD)


def getSizeForCount(count):
    bits = getBits(count)
    if not bits:
        return 1
    elif not (bits % 32):
        return bits
    else:
        return bits + 1


class RegisterSet(object):
    def __init__(self, count):
        self.count = count
        self.M = [0 for _ in range(getSizeForCount(self.count))]
        self.size = len(self.M)

    def set(self, position, value):
        bucketPos = int(position / LOG2_BITS_PER_WORD)
        shift = REGISTER_SIZE * (position - (bucketPos * LOG2_BITS_PER_WORD))
        self.M[bucketPos] = (
            self.M[bucketPos] & ~(0x1f << shift) | (value << shift))

    def get(self, position):
        bucketPos = int(position / LOG2_BITS_PER_WORD)
        shift = REGISTER_SIZE * (position - (bucketPos * LOG2_BITS_PER_WORD))
        return ((self.M[bucketPos] & (0x1f << shift)) % 0x100000000) >> shift

    def updateIfGreater(self, position, value):
        bucket = int(position / LOG2_BITS_PER_WORD)
        shift = REGISTER_SIZE * (position - (bucket * LOG2_BITS_PER_WORD))
        mask = 0x1f << shift

        curVal = self.M[bucket] & mask
        newVal = value << shift
        if curVal < newVal:
            self.M[bucket] = (self.M[bucket] & ~mask) | newVal
            return True
        else:
            return False

    def merge(self, that):
        for bucket, m in enumerate(self.M):
            word = 0
            for j in range(LOG2_BITS_PER_WORD):
                mask = 0x1f << (REGISTER_SIZE * j)
                thisVal = (self.M[bucket] & mask)
                thatVal = (that.M[bucket] & mask)
                word |= thatVal if thisVal < thatVal else thisVal
            self.M[bucket] = word

    def readOnlyBits(self):
        return self.M
