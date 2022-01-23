"""
Nozomi
Random Number Module
Copyright Amatino Pty Ltd
"""
from nozomi.ancillary.immutable import Immutable
from os import urandom
from base64 import b64encode, urlsafe_b64encode
import sys


class RandomNumber:
    """A cryptographically secure random number"""

    def __init__(self, bit_length: int):

        assert isinstance(bit_length, int)
        self._number = urandom(int(bit_length / 8))
        return

    utf8_bytes = Immutable(lambda s: str(s.integer))
    integer = Immutable(lambda s: int.from_bytes(
        s._number,
        byteorder=sys.byteorder
    ))
    base64 = Immutable(lambda s: b64encode(s._number).decode('utf-8'))
    urlsafe_base64 = Immutable(
        lambda s: urlsafe_b64encode(s._number).decode('utf-8')
    )
    dash_free_urlsafe_base64 = Immutable(
        lambda s: s.urlsafe_base64.replace('-', 'X').replace('_', 'Y')
    )
    clean_base64 = Immutable(
        lambda s: s.dash_free_urlsafe_base64.replace('=', '')
    )
