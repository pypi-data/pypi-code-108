BYTE_MIN_VALUE = -128
BYTE_MAX_VALUE = 127
SHORT_MIN_VALUE = -32768
SHORT_MAX_VALUE = 32767
INT3_MIN_VALUE = -0x800000
INT3_MAX_VALUE = 0x007fffff
INT_MIN_VALUE = -0x80000000
INT_MAX_VALUE = 0x7fffffff
LONG5_MIN_VALUE = -0x8000000000
LONG5_MAX_VALUE = 0x0000007fffffffff
LONG_MIN_VALUE = -0x8000000000000000
LONG_MAX_VALUE = 0x7fffffffffffffff


class BitUtil(object):
    @staticmethod
    def composite(hkey, wkey):
        if BYTE_MIN_VALUE <= wkey <= BYTE_MAX_VALUE:
            return (hkey << 8) | (wkey & 0xff)
        elif SHORT_MIN_VALUE <= wkey <= SHORT_MAX_VALUE:
            return (hkey << 16) | (wkey & 0xffff)
        elif INT_MIN_VALUE <= wkey <= INT_MAX_VALUE:
            return (hkey << 32) | (wkey & 0xffffffff)

    @staticmethod
    def setHigh(src, hkey):
        return (src & 0x00000000ffffffff) | (hkey << 32)

    @staticmethod
    def setLow(src, wkey):
        return (src & 0xffffffff00000000) | (wkey & 0xffffffff)

    @staticmethod
    def getHigh(key):
        if SHORT_MIN_VALUE <= key <= SHORT_MAX_VALUE:
            return ((key >> 8) % 0x100000000) & 0xff
        elif INT_MIN_VALUE <= key <= INT_MAX_VALUE:
            return ((key >> 16) % 0x100000000) & 0xffff
        elif LONG_MIN_VALUE <= key <= LONG_MAX_VALUE:
            return ((key >> 32) % 0x100000000) & 0xffffffff

    @staticmethod
    def getLow(key):
        if SHORT_MIN_VALUE <= key <= SHORT_MAX_VALUE:
            return key & 0xff
        elif INT_MIN_VALUE <= key <= INT_MAX_VALUE:
            return key & 0xffff
        elif LONG_MIN_VALUE <= key <= LONG_MAX_VALUE:
            return key & 0xffffffff
