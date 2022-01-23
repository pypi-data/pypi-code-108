"""
Nozomi
Access Control Module
author: hugh@blinkybeach.com
"""
from nozomi.ancillary.immutable import Immutable
from nozomi.ancillary.configuration import Configuration
from nozomi.http.headers import Headers


class AccessControl:
    """
    The headers, methods, and other HTTP Access Control data that define
    access allowed by a browser.
    """
    _ALLOWED_METHODS = 'GET,PUT,POST,OPTIONS,DELETE'
    _ALLOW_CREDENTIALS = 'true'
    _ALLOWED_HEADERS = ['cookie', 'accept', 'content-type']

    def __init__(self, configuration: Configuration) -> None:

        assert isinstance(configuration, Configuration)
        self._configuration = configuration
        return

    _allowed_headers = Immutable(
        lambda s: ','.join(s._ALLOWED_HEADERS + [
            s._configuration.session_id_name,
            s._configuration.session_cookie_key_name,
            s._configuration.session_api_key_name
        ])
    )

    def apply_to_headers(self, headers: Headers) -> Headers:
        """
        Apply access control headerst to the supplied headers and return them.
        """
        headers.add(
            'Access-Control-Allow-Headers',
            self._allowed_headers
        )
        headers.add(
            'Access-Control-Allow-Methods',
            self._ALLOWED_METHODS
        )
        headers.add(
            'Access-Control-Allow-Credentials',
            self._ALLOW_CREDENTIALS
        )
        return headers
