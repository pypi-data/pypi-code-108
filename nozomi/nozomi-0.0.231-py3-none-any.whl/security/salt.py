"""
Nozomi
Salt Module
Copyright Amatino Pty Ltd
"""
from nozomi.security.random_number import RandomNumber
from nozomi.ancillary.immutable import Immutable
from typing import TypeVar
from typing import Type

T = TypeVar('T', bound='Salt')


class Salt:
    """A cryptographically secure salt for use in passphrase hashing"""

    _SALT_LENGTH = 64

    def __init__(self, salt_b64_string: str) -> None:

        assert isinstance(salt_b64_string, str)
        self._b64_string = salt_b64_string
        return

    string = Immutable(lambda s: str(s))
    utf8_bytes = Immutable(lambda s: str(s).encode('utf-8'))

    def __str__(self) -> str:
        return self._b64_string

    @classmethod
    def create(cls: Type[T]) -> T:
        """Return a new cryptographically secure Salt"""
        return cls(RandomNumber(cls._SALT_LENGTH).base64)
