"""
Nozomi
HTTP Headers Module
Copyright Amatino Pty Ltd
"""
from typing import Optional, List
from collections.abc import Mapping
from nozomi.errors.error import NozomiError
from nozomi.ancillary.immutable import Immutable
from nozomi.http.status_code import HTTPStatusCode
from nozomi.http.abstract_headers import AbstractHeaders


class Headers(AbstractHeaders):
    """
    A set of HTTP headers. Feed Headers a Mapping-conformant data type, for
    example a Dict or a Werkzeug ImmutableMultiDict.
    """
    _TYPE_ERROR = 'The data structure underlying a Headers instance \
unexpectedly contained non-string data for key "{k}", of type {t}. Headers \
must only contain string values. Consider examining the data you fed to the \
Headers initialiser.'

    def __init__(self, raw: Mapping = {}) -> None:
        self._raw = raw
        return

    dictionary = Immutable(lambda s: s._raw)

    def value_for(self, key: str) -> Optional[str]:
        """
        Return the value of a supplied header key, or None if no value
        exists for that key.
        """
        value = self._raw.get(key)
        if value is None:

            for item in self._raw:
                if isinstance(item, tuple) and len(item) > 1:
                    if isinstance(item[0], str):
                        if item[0].lower() == key.lower():
                            return item[1]
                if isinstance(item, str) and item.lower() == key.lower():
                    return self._raw[key.lower()]

            return None

        if not isinstance(value, str):
            raise NozomiError(
                self._TYPE_ERROR.format(
                    k=key,
                    t=str(type(value))
                ),
                HTTPStatusCode.BAD_REQUEST
            )

        return value

    def getlist(self, key: str) -> List[str]:

        if not hasattr(self._raw, 'getlist'):
            return list()

        return self._raw.getlist(key)

    def add(self, key: str, value: str) -> None:
        if (hasattr(self._raw, 'add')):
            self._raw.add(key, value)
            return
        self._raw[key] = value
        return
