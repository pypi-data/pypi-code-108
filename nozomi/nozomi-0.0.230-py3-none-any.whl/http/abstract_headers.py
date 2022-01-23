"""
Nozomi
Abstract HTTP Headers Module
Copyright Amatino Pty Ltd
"""
from typing import Optional, List
from collections.abc import Mapping
from nozomi.ancillary.immutable import Immutable


class AbstractHeaders:
    """
    A set of HTTP headers. Feed Headers a Mapping-conformant data type, for
    example a Dict or a Werkzeug ImmutableMultiDict.
    """

    def __init__(self, raw: Mapping = {}) -> None:
        self._raw = raw
        return

    dictionary = Immutable(lambda s: s._raw)

    def value_for(self, key: str) -> Optional[str]:
        """
        Return the value of a supplied header key, or None if no value
        exists for that key.
        """
        raise NotImplementedError

    def getlist(self, key: str) -> List[str]:
        raise NotImplementedError

    def add(self, key: str, value: str) -> None:
        raise NotImplementedError
