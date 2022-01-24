"""
Module representing the core data and datatype limits required by the BBM controller.
"""

MATES_COMMAND_START_BYTE = '$'

MATES_BOOT_TIMEOUT = 5000
MATES_STRING_BUFFER_SIZE = 250
MATES_STRING_MAX_BUFFER_SIZE = 32000 # max allowable is 32767 but usually not required anyway
MATES_SAFE_ACK = 0x06
MATES_RESPONSE_TIMEOUT = 500 # ms

MATES_MIN_BACKLIGHT = 0
MATES_MAX_BACKLIGHT = 15

CHAR_BYTE_LENGTH = 1
WORD_BYTE_LENGTH = 2
INT_BYTE_LENGTH  = 4

UINT_8_MIN = 0
UINT_8_MAX = 255            # 2**8 - 1

INT_8_MIN = -128            # -(2**8)/2
INT_8_MAX = 127             # (2**8)/2 - 1

UINT_16_MIN = 0
UINT_16_MAX = 65535         # 2**16 - 1

INT_16_MIN = -32768         # -(2**16)/2
INT_16_MAX = 32767          # (2**16)/2 - 1

UINT_32_MIN = 0
UINT_32_MAX = 4294967295    # 2**32 - 1

INT_32_MIN = -2147483648    # -(2**32)/2
INT_32_MAX = 2147483647     # (2**32)/2 - 1

FLOAT_32_MIN = -2**128
FLOAT_32_MAX = 2**128

UINT8 = 'uint8'
INT8 = 'int8'
UINT16 = 'uint16'
INT16 = 'int16'
UINT32 = 'uint32'
INT32 = 'int32'
FLOAT32 = 'float32'

datatype_ranges = {}
datatype_ranges[UINT8] = (UINT_8_MIN, UINT_8_MAX)
datatype_ranges[INT8] = (INT_8_MIN, INT_8_MAX)
datatype_ranges[UINT16] = (UINT_16_MIN, UINT_16_MAX)
datatype_ranges[INT16] = (INT_16_MIN, INT_16_MAX)
datatype_ranges[UINT32] = (UINT_32_MIN, UINT_32_MAX)
datatype_ranges[INT32] = (INT_32_MIN, INT_32_MAX)
datatype_ranges[FLOAT32] = (FLOAT_32_MIN, FLOAT_32_MAX)


if __name__ == '__main__':
    print(datatype_ranges)
