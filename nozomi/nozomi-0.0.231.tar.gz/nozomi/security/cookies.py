"""
Nozomi
Cookies Module
author: hugh@blinkybeach.com
"""
from nozomi.http.headers import Headers
from nozomi.ancillary.immutable import Immutable
from typing import TypeVar, Type, Dict, Optional

T = TypeVar('T', bound='Cookies')


class Cookies:
    """An instance of a set of cookies sent by a client"""

    def __init__(self, raw_cookies: str) -> None:

        self._cookies: Dict[str, str] = dict()
        self._raw_cookies = raw_cookies

        if raw_cookies is None:
            return

        for cookie in raw_cookies.split(';'):
            pieces = cookie.strip().split('=')
            try:
                self._cookies[pieces[0]] = pieces[1]
            except IndexError:
                raise RuntimeError('Invalid cookies supplied')

        return

    is_empty: bool = Immutable(lambda s: len(s._cookies) < 1)

    def contains(self, cookie_name: str) -> bool:
        """Return true if the jar contains the specified cookie"""
        if cookie_name in self._cookies.keys():
            return True
        return False

    def value_for(self, cookie_name: str) -> str:
        """
        Return the value of a specified cookie
        """
        if self.contains(cookie_name) is False:
            raise ValueError('Cookie with specified name does not exist')
        return self._cookies[cookie_name]

    @classmethod
    def from_headers(cls: Type[T], headers: Headers) -> Optional[T]:
        """Return Cookies parsed from request headers"""
        raw_cookies = headers.value_for('Cookie')
        if raw_cookies is None:
            return None
        return cls(raw_cookies)
