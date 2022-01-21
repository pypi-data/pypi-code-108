"""
Implemented some functions which are used in the code decompiled by IDA.
"""

from .types import int8, int16, int32, \
    uint8, uint16, uint32, uint64, \
    IntTypes
from .utils import get_size, get_signed, get_type, offset_n

BIG_ENDIAN = 'big'
LITTLE_ENDIAN = 'little'

# default use little endian
BYTE_ORDER = LITTLE_ENDIAN


def last_ind(x: IntTypes, part_type: type) -> int:
    """Implementation for `LAST_IND`."""
    return get_size(x) // get_size(part_type) - 1


def low_ind(
        x: IntTypes,
        part_type: type,
        byteorder: str = LITTLE_ENDIAN
) -> int:
    """Implementation for `LOW_IND`."""
    return last_ind(x, part_type) if byteorder == BIG_ENDIAN else 0


def high_ind(
        x: IntTypes,
        part_type: type,
        byteorder: str = LITTLE_ENDIAN
) -> int:
    """Implementation for `HIGH_IND`."""
    return 0 if byteorder == BIG_ENDIAN else last_ind(x, part_type)


def byte_n(x: IntTypes, n: int) -> uint8:
    """Implementation for `BYTEn`."""
    return offset_n(x, n, uint8, BYTE_ORDER)


def word_n(x: IntTypes, n: int) -> uint16:
    """Implementation for `WORDn`."""
    return offset_n(x, n, uint16, BYTE_ORDER)


def dword_n(x: IntTypes, n: int) -> uint32:
    """Implementation for `DWORDn`."""
    return offset_n(x, n, uint32, BYTE_ORDER)


def low_byte(x: IntTypes) -> uint8:
    """Implementation for `LOBYTE`."""
    return byte_n(x, low_ind(x, uint8))


def low_word(x: IntTypes) -> uint16:
    """Implementation for `LOWORD`."""
    return word_n(x, low_ind(x, uint16))


def low_dword(x: IntTypes) -> uint32:
    """Implementation for `LODWORD`."""
    return dword_n(x, low_ind(x, uint32))


def high_byte(x: IntTypes) -> uint8:
    """Implementation for `HIBYTE`."""
    return byte_n(x, high_ind(x, uint8))


def high_word(x: IntTypes) -> uint16:
    """Implementation for `HIWORD`."""
    return word_n(x, high_ind(x, uint16))


def high_dword(x: IntTypes) -> uint32:
    """Implementation for `HIDWORD`."""
    return dword_n(x, high_ind(x, uint32))


def byte1(x: IntTypes) -> uint8:
    """Implementation for `BYTE1`."""
    return byte_n(x, 1)


def byte2(x: IntTypes) -> uint8:
    """Implementation for `BYTE2`."""
    return byte_n(x, 2)


def byte3(x: IntTypes) -> uint8:
    """Implementation for `BYTE3`."""
    return byte_n(x, 3)


def byte4(x: IntTypes) -> uint8:
    """Implementation for `BYTE4`."""
    return byte_n(x, 4)


def byte5(x: IntTypes) -> uint8:
    """Implementation for `BYTE5`."""
    return byte_n(x, 5)


def byte6(x: IntTypes) -> uint8:
    """Implementation for `BYTE6`."""
    return byte_n(x, 6)


def byte7(x: IntTypes) -> uint8:
    """Implementation for `BYTE7`."""
    return byte_n(x, 7)


def byte8(x: IntTypes) -> uint8:
    """Implementation for `BYTE8`."""
    return byte_n(x, 8)


def byte9(x: IntTypes) -> uint8:
    """Implementation for `BYTE9`."""
    return byte_n(x, 9)


def byte10(x: IntTypes) -> uint8:
    """Implementation for `BYTE10`."""
    return byte_n(x, 10)


def byte11(x: IntTypes) -> uint8:
    """Implementation for `BYTE11`."""
    return byte_n(x, 11)


def byte12(x: IntTypes) -> uint8:
    """Implementation for `BYTE12`."""
    return byte_n(x, 12)


def byte13(x: IntTypes) -> uint8:
    """Implementation for `BYTE13`."""
    return byte_n(x, 13)


def byte14(x: IntTypes) -> uint8:
    """Implementation for `BYTE14`."""
    return byte_n(x, 14)


def byte15(x: IntTypes) -> uint8:
    """Implementation for `BYTE15`."""
    return byte_n(x, 15)


def word1(x: IntTypes) -> uint8:
    """Implementation for `WORD1`."""
    return word_n(x, 1)


def word2(x: IntTypes) -> uint8:
    """Implementation for `WORD2`."""
    return word_n(x, 2)


def word3(x: IntTypes) -> uint8:
    """Implementation for `WORD3`."""
    return word_n(x, 3)


def word4(x: IntTypes) -> uint8:
    """Implementation for `WORD4`."""
    return word_n(x, 4)


def word5(x: IntTypes) -> uint8:
    """Implementation for `WORD5`."""
    return word_n(x, 5)


def word6(x: IntTypes) -> uint8:
    """Implementation for `WORD6`."""
    return word_n(x, 6)


def word7(x: IntTypes) -> uint8:
    """Implementation for `WORD7`."""
    return word_n(x, 7)


def signed_byte_n(x: IntTypes, n: int) -> int8:
    """Implementation for `SBYTEn`."""
    return offset_n(x, n, int8, BYTE_ORDER)


def signed_word_n(x: IntTypes, n: int) -> int16:
    """Implementation for `SWORDn`."""
    return offset_n(x, n, int16, BYTE_ORDER)


def signed_dword_n(x: IntTypes, n: int) -> int32:
    """Implementation for `SDWORDn`."""
    return offset_n(x, n, int32, BYTE_ORDER)


def signed_low_byte(x: IntTypes) -> int8:
    """Implementation for `SLOBYTE`."""
    return signed_byte_n(x, low_ind(x, int8))


def signed_low_word(x: IntTypes) -> int16:
    """Implementation for `SLOWORD`."""
    return signed_word_n(x, low_ind(x, int16))


def signed_low_dword(x: IntTypes) -> int32:
    """Implementation for `SLODWORD`."""
    return signed_dword_n(x, low_ind(x, int32))


def signed_high_byte(x: IntTypes) -> int8:
    """Implementation for `SHIBYTE`."""
    return signed_byte_n(x, high_ind(x, int8))


def signed_high_word(x: IntTypes) -> int16:
    """Implementation for `SHIWORD`."""
    return signed_word_n(x, high_ind(x, int16))


def signed_high_dword(x: IntTypes) -> int32:
    """Implementation for `SHIDWORD`."""
    return signed_dword_n(x, high_ind(x, int32))


def signed_byte1(x: IntTypes) -> int8:
    """Implementation for `SBYTE1`."""
    return signed_byte_n(x, 1)


def signed_byte2(x: IntTypes) -> int8:
    """Implementation for `SBYTE2`."""
    return signed_byte_n(x, 2)


def signed_byte3(x: IntTypes) -> int8:
    """Implementation for `SBYTE3`."""
    return signed_byte_n(x, 3)


def signed_byte4(x: IntTypes) -> int8:
    """Implementation for `SBYTE4`."""
    return signed_byte_n(x, 4)


def signed_byte5(x: IntTypes) -> int8:
    """Implementation for `SBYTE5`."""
    return signed_byte_n(x, 5)


def signed_byte6(x: IntTypes) -> int8:
    """Implementation for `SBYTE6`."""
    return signed_byte_n(x, 6)


def signed_byte7(x: IntTypes) -> int8:
    """Implementation for `SBYTE7`."""
    return signed_byte_n(x, 7)


def signed_byte8(x: IntTypes) -> int8:
    """Implementation for `SBYTE8`."""
    return signed_byte_n(x, 8)


def signed_byte9(x: IntTypes) -> int8:
    """Implementation for `SBYTE9`."""
    return signed_byte_n(x, 9)


def signed_byte10(x: IntTypes) -> int8:
    """Implementation for `SBYTE10`."""
    return signed_byte_n(x, 10)


def signed_byte11(x: IntTypes) -> int8:
    """Implementation for `SBYTE11`."""
    return signed_byte_n(x, 11)


def signed_byte12(x: IntTypes) -> int8:
    """Implementation for `SBYTE12`."""
    return signed_byte_n(x, 12)


def signed_byte13(x: IntTypes) -> int8:
    """Implementation for `SBYTE13`."""
    return signed_byte_n(x, 13)


def signed_byte14(x: IntTypes) -> int8:
    """Implementation for `SBYTE14`."""
    return signed_byte_n(x, 14)


def signed_byte15(x: IntTypes) -> int8:
    """Implementation for `SBYTE15`."""
    return signed_byte_n(x, 15)


def signed_word1(x: IntTypes) -> int8:
    """Implementation for `SWORD1`."""
    return signed_word_n(x, 1)


def signed_word2(x: IntTypes) -> int8:
    """Implementation for `SWORD2`."""
    return signed_word_n(x, 2)


def signed_word3(x: IntTypes) -> int8:
    """Implementation for `SWORD3`."""
    return signed_word_n(x, 3)


def signed_word4(x: IntTypes) -> int8:
    """Implementation for `SWORD4`."""
    return signed_word_n(x, 4)


def signed_word5(x: IntTypes) -> int8:
    """Implementation for `SWORD5`."""
    return signed_word_n(x, 5)


def signed_word6(x: IntTypes) -> int8:
    """Implementation for `SWORD6`."""
    return signed_word_n(x, 6)


def signed_word7(x: IntTypes) -> int8:
    """Implementation for `SWORD7`."""
    return signed_word_n(x, 7)


def pair(high: IntTypes, low: IntTypes) -> IntTypes:
    """Implementation for `__PAIR__`."""
    size = get_size(high)
    signed = get_signed(high)
    int_type = get_type(size=size * 2, signed=signed)
    return int_type(high) << size * 8 | type(high)(low)


def rol(value: IntTypes, count: int) -> IntTypes:
    """Implementation for `__ROL__`."""
    dtype = type(value)
    nbits = get_size(value) * 8

    if count > 0:
        count %= nbits
        high = value >> (nbits - count)
        if get_signed(value):
            high &= ~(dtype(-1) << count)
        value <<= count
        value |= high

    else:
        count = -count % nbits
        low = value << (nbits - count)
        value >>= count
        value |= low

    return value


def rol1(value: IntTypes, count: int) -> uint8:
    """Implementation for `__ROL1__`."""
    return rol(uint8(value), count)


def rol2(value: IntTypes, count: int) -> uint16:
    """Implementation for `__ROL2__`."""
    return rol(uint16(value), count)


def rol4(value: IntTypes, count: int) -> uint32:
    """Implementation for `__ROL4__`."""
    return rol(uint32(value), count)


def rol8(value: IntTypes, count: int) -> uint64:
    """Implementation for `__ROL8__`."""
    return rol(uint64(value), count)


def ror1(value: IntTypes, count: int) -> uint8:
    """Implementation for `__ROR1__`."""
    return rol(uint8(value), -count)


def ror2(value: IntTypes, count: int) -> uint16:
    """Implementation for `__ROR2__`."""
    return rol(uint16(value), -count)


def ror4(value: IntTypes, count: int) -> uint32:
    """Implementation for `__ROR4__`."""
    return rol(uint32(value), -count)


def ror8(value: IntTypes, count: int) -> uint64:
    """Implementation for `__ROR8__`."""
    return rol(uint64(value), -count)


def mkcshl(value: IntTypes, count: int) -> int8:
    """Implementation for `__MKCSHL__`."""
    nbits = get_size(value) * 8
    count %= nbits
    return (value >> (nbits - count)) & 1


def mkcshr(value: IntTypes, count: int) -> int8:
    """Implementation for `__MKCSHR__`."""
    return (value >> (count - 1)) & 1


def sets(x: IntTypes) -> int8:
    """Implementation for `__SETS__`."""
    return int8(x < 0)


def ofsub(x: IntTypes, y: IntTypes) -> IntTypes:
    """Implementation for `__OFSUB__`."""
    if get_size(x) < get_size(y):
        x2 = x
        sx = sets(x2)
        return (sx ^ sets(y)) & (sx ^ sets(x2 - y))
    else:
        y2 = y
        sx = sets(x)
        return (sx ^ sets(y2)) & (sx ^ sets(x - y2))


def ofadd(x: IntTypes, y: IntTypes) -> IntTypes:
    """Implementation for `__OFADD__`."""
    if get_size(x) < get_size(y):
        x2 = x
        sx = sets(x2)
        return ((1 ^ sx) ^ sets(y)) & (sx ^ sets(x2 + y))
    else:
        y2 = y
        sx = sets(x)
        return ((1 ^ sx) ^ sets(y2)) & (sx ^ sets(x + y2))


def cfsub(x: IntTypes, y: IntTypes) -> int8:
    """Implementation for `__CFSUB__`."""
    return int8(x < y)


def cfadd(x: IntTypes, y: IntTypes) -> int8:
    """Implementation for `__CFADD__`."""
    return int8(x > y)


# define reference names

LAST_IND = last_ind
LOW_IND = low_ind
HIGH_IND = high_ind

BYTEN = byte_n
WORDN = word_n
DWORDN = dword_n

LOBYTE = low_byte
LOWORD = low_word
LODWORD = low_dword
HIBYTE = high_byte
HIWORD = high_word
HIDWORD = high_dword
BYTE1 = byte1
BYTE2 = byte2
BYTE3 = byte3
BYTE4 = byte4
BYTE5 = byte5
BYTE6 = byte6
BYTE7 = byte7
BYTE8 = byte8
BYTE9 = byte9
BYTE10 = byte10
BYTE11 = byte11
BYTE12 = byte12
BYTE13 = byte13
BYTE14 = byte14
BYTE15 = byte15
WORD1 = word1
WORD2 = word2
WORD3 = word3
WORD4 = word4
WORD5 = word5
WORD6 = word6
WORD7 = word7

SBYTEN = signed_byte_n
SWORDN = signed_word_n
SDWORDN = signed_dword_n

SLOBYTE = signed_low_byte
SLOWORD = signed_low_word
SLODWORD = signed_low_dword
SHIBYTE = signed_high_byte
SHIWORD = signed_high_word
SHIDWORD = signed_high_dword
SBYTE1 = signed_byte1
SBYTE2 = signed_byte2
SBYTE3 = signed_byte3
SBYTE4 = signed_byte4
SBYTE5 = signed_byte5
SBYTE6 = signed_byte6
SBYTE7 = signed_byte7
SBYTE8 = signed_byte8
SBYTE9 = signed_byte9
SBYTE10 = signed_byte10
SBYTE11 = signed_byte11
SBYTE12 = signed_byte12
SBYTE13 = signed_byte13
SBYTE14 = signed_byte14
SBYTE15 = signed_byte15
SWORD1 = signed_word1
SWORD2 = signed_word2
SWORD3 = signed_word3
SWORD4 = signed_word4
SWORD5 = signed_word5
SWORD6 = signed_word6
SWORD7 = signed_word7

__PAIR__ = pair

__ROL1__ = rol1
__ROL2__ = rol2
__ROL4__ = rol4
__ROL8__ = rol8
__ROR1__ = ror1
__ROR2__ = ror2
__ROR4__ = ror4
__ROR8__ = ror8

__MKCSHL__ = mkcshl
__MKCSHR__ = mkcshr

__SETS__ = sets

__OFSUB__ = ofsub
__OFADD__ = ofadd
__CFSUB__ = cfsub
__CFADD__ = cfadd
