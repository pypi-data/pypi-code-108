"""
Python 2 and 3 compatible function
"""
import sys
import base64
import binascii
# check python version in use
PY3 = sys.version_info[0] >= 3
ENCODING = 'latin-1'


# It is internal function. Only call it from if PY3: block


def _to_bytes(s):
    if s is None:
        return s

    if type(s) is str:
        s = s.encode(ENCODING)
    return s


def b64_encode(s):
    if s is None:
        return s

    if PY3:
        return base64.b64encode(_to_bytes(s)).decode(ENCODING)

    return base64.b64encode(s)


def b64_decode(s):
    if s is None:
        return s

    if PY3:
        # signature, wrap and aes operation was failing without 'latin-1'
        # 'latin-1' make python3 to behave like python2 for encoding/decoding
        return base64.b64decode(_to_bytes(s)).decode(ENCODING)

    return base64.b64decode(s)


def read_binary(in_f=None, mode='rb'):
    buff = None
    if in_f is None:
        if PY3:
            buff = sys.stdin.buffer.read()
        else:
            buff = sys.stdin.read()
    else:
        with open(in_f, mode) as f:
            buff = f.read()

    return buff


def hex_decode(hex_str):
    if hex_str is None:
        return hex_str

    if PY3:
        return binascii.unhexlify(_to_bytes(hex_str.strip())).decode(ENCODING)

    return binascii.unhexlify(hex_str.strip())


def hex_encode(s):
    if s is None:
        return s

    if PY3:
        return binascii.hexlify(_to_bytes(s)).decode(ENCODING)

    return binascii.hexlify(s)

# As we are opening file in wb mode, Python3 require data type should be byte to write


def to_bytes(s):
    if s is None:
        return s

    if type(s) is bytes or type(s) is bytearray:
        return s

    if PY3:
        return bytes(s, encoding=ENCODING)

    return bytes(s)


def to_string(s):
    if s is None:
        return s
    if type(s) is str:
        return s

    if type(s) is bytearray:
        return s.decode(encoding=ENCODING)

    return s

def to_byte_array(s):
    if s is None:
        return s

    if PY3:
        if type(s) is bytearray:
            return s
        if type(s) is str:
            return bytearray(s, encoding=ENCODING)
        return bytearray(s)

    return bytearray(s)

