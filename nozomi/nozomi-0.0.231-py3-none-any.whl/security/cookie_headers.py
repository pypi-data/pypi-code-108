"""
Nozomi
Cookie Headers module
author: hugh@blinkybeach.com
"""
from nozomi.http.headers import Headers
from nozomi.security.abstract_session import AbstractSession as Session
from nozomi.ancillary.configuration import Configuration
from nozomi.ancillary.immutable import Immutable
from typing import Optional
from typing import TypeVar, Type
from collections.abc import Mapping

T = TypeVar('T', bound='CookieHeaders')


class CookieHeaders(Headers):
    """
    A set of HTTP request headers that include cookie data
    for a supplied Session
    """
    def __init__(
        self,
        session: Session,
        configuration: Configuration,
        existing: Optional[Headers] = None
    ) -> None:

        assert isinstance(session, Session)
        self._debug = configuration.debug
        self._configuration = configuration
        self._session = session

        headers = Headers()
        if existing is not None:
            assert isinstance(existing, Headers)
            headers = existing

        headers.add('Set-Cookie', self._generate_session_cookie(self._debug))
        headers.add('Set-Cookie', self._generate_key_cookie(self._debug))
        headers.add('Set-Cookie', self.generate_flag_cookie(
            logged_in=True,
            debug=configuration.debug,
            configuration=configuration
        ))

        self._raw = headers.dictionary

        super().__init__(headers)
        return

    dictionary = Immutable(lambda s: s._raw.dictionary)

    def add_to(self, other: Mapping) -> Mapping:
        for key in self._raw.keys():
            other[key] = self._raw[key]
        return other

    def _generate_session_cookie(self, debug: bool = False) -> str:
        """Return a set cookie string"""
        id_name = self._configuration.session_id_name
        cookie = id_name + '=' + str(self._session.session_id)
        cookie += self._cookie_options(debug)
        return cookie

    def _generate_key_cookie(self, debug: bool = False) -> str:
        key_name = self._configuration.session_cookie_key_name
        cookie = key_name + '=' + str(self._session.session_key)
        cookie += self._cookie_options(debug)
        return cookie

    def _cookie_options(self, debug: bool = False) -> str:
        """Return shared cookie options"""
        options = '; Path=/; HttpOnly; SameSite=Strict'
        if debug is False:  # We can't set secure in the debug HTTP environment
            options += '; Secure'
        return options

    def simulate_cookie(self, debug: bool = True) -> str:
        cookie = Session.ID_NAME + '=' + str(self._session.session_id)
        cookie += ';' + Session.KEY_NAME + '=' + self._session.session_key
        return cookie

    def simulate_cookie_headers(self, debug: bool = True) -> Headers:
        headers = Headers()
        headers.add(
            'Cookie',
            self.simulate_cookie(debug)
        )
        return headers

    @classmethod
    def generate_flag_cookie(
        cls: Type[T],
        logged_in: bool,
        debug: bool,
        configuration: Configuration
    ) -> str:

        cookie_name = configuration.session_flag_cookie_name

        def compute_value(logged_in: bool) -> str:
            if logged_in is True:
                return '1'
            return '0'

        options = '; Path=/; SameSite=Strict;'
        if debug is False:
            options += '; Secure'
        cookie = cookie_name + '=' + compute_value(logged_in)
        return cookie + options

    @classmethod
    def flag_signout(
        cls: Type[T],
        debug: bool,
        configuration: Configuration,
        existing_headers: Optional[Headers] = None
    ) -> Headers:

        existing = existing_headers

        headers = Headers()
        if existing is not None:
            assert isinstance(existing, Headers)
            headers = existing

        headers.add('Set-Cookie', cls.generate_flag_cookie(
            logged_in=False,
            debug=debug,
            configuration=configuration
        ))

        return headers
