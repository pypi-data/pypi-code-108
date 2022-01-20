"""
Data encoding and decoding

.. py:data:: ENCODINGS

   List of all supported encodings

"""

import quopri
import base64
import typing
from pathlib import PurePosixPath

from . import ascii

__all__ = [
    'is_printable',
    'quopri_decode', 'quopri_encode',
    'encode_data', 'decode_data',
    'make_pure_ascii',
    'encode_posix_path'
]


ENCODINGS = ['base64', 'quopri']

# Consider these control characters 'printable' with quopri module
ALLOWED_CTRL_CHRS = {
    ascii.BEL,
    ascii.BS,
    ascii.TAB,
    ascii.HT,
    ascii.LF,
    ascii.VT,
    ascii.FF,
    ascii.CR,
    ascii.ESC,
    ascii.DEL,
}


def is_printable(s: bytes, low: int = ascii.SP, allowed: set = None):
    """ Detect if string is printable; it should not contain any control characters, except those
    in `allowed`, and less than 5% of the characters are allowed to be high-ascii
    """
    if allowed is None:
        allowed = set()

    highcount = 0

    for c in s:
        if c not in allowed:
            if c < low:
                return False
            if c >= ascii.DEL:
                highcount += 1

    return highcount == 0 or (len(s) / highcount >= 20)


def is_newline(c: int):
    return c in (ascii.LF, ascii.CR)


ASCII_EQUALS = ord('=')


def quopri_encode(data: typing.Union[str, bytes]):
    """ Encode data using quoted printable method
    Uses a different algorithm than :py:func:`quopri.encodestring`:

    * Encodes first space character on a line, but not the rest
    * Encodes newline, return characters and high-ascii
    """
    if isinstance(data, str):
        data = data.encode('utf-8', 'replace')

    result = ''
    lc, encode_low, encode_high, linesz = None, ascii.SP, ascii.DEL, 0

    for c in data:
        if linesz > 77 or (is_newline(lc) and (c == lc or not is_newline(c))):
            result += '=\n'
            encode_low, linesz = ascii.SP, 0

        if c <= encode_low or c == ASCII_EQUALS or c >= encode_high:
            result += '=%02X' % c
            linesz += 3
        else:
            result += chr(c)
            linesz += 1

        lc, encode_low = c, ascii.US

    if lc == ' ':
        result += '='

    return result


def quopri_decode(data):
    """ Decode quoted printable data
    """
    clean_data = '\n'.join([line.lstrip() for line in data.split("\n")])
    return quopri.decodestring(clean_data)


def encode_data(data: typing.Union[str, bytes]) -> typing.Tuple[str, str]:
    """ Encode provided data.

    Printable data is encoded using *Quoted-printable* encoding, any other data is
    encoded using *Base64* encoding.

    :param str data: Data to encode
    :rtype: tuple
    :return: tuple(encoded, encoding)

             * *encoded*: The encoded data
             * *encoding* (str): The encoding used. ``quopri`` or ``base64``
    """
    if isinstance(data, str):
        data = data.encode('utf-8', 'replace')

    if is_printable(data, allowed=ALLOWED_CTRL_CHRS):
        encoding = 'quopri'
        encoded = quopri_encode(data)

    else:
        encoding = 'base64'
        # noinspection PyTypeChecker
        encoded = base64.b64encode(data).decode('ascii')

    return encoded, encoding


def decode_data(data: str, encoding: str) -> bytes:
    """ Decode encoded data.

    :param data: Data to decode
    :param encoding: The encoding used on the data: ``quopri`` or ``base64``
    :return: The decoded data
    :raise ValueError: For unsupported encodings
    """
    if encoding == 'quopri':
        return quopri_decode(data)

    elif encoding == 'base64':
        # noinspection PyTypeChecker
        return base64.b64decode(data)

    raise ValueError('Unsupported encoding')


def make_pure_ascii(s: str) -> str:
    parts = s.split('.')
    result = []
    for part in parts:
        try:
            result.append(part.encode('ascii'))
        except UnicodeEncodeError:
            result.append(part.encode('punycode'))

    return (b'.'.join(result)).decode('ascii')


def encode_posix_path(path: PurePosixPath) -> PurePosixPath:
    """ Encode a path using idna encoding to ensure it will only contain ascii characters """

    return PurePosixPath(*(
        make_pure_ascii(part) for part in path.parts
    ))
