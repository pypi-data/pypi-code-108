"""
Nozomi
Cross-Origin-Resource-Sharing Policy
author: hugh@blinkybeach.com
"""
from nozomi.ancillary.configuration import Configuration
from nozomi.ancillary.immutable import Immutable
from nozomi.http.headers import Headers


class CORSPolicy:
    """
    Policy on Cross-Origin-Resource-Sharing, aka what origins may make requests
    to the application in the browser.
    """
    _ALL_ORIGINS = '*'
    _HEADER_KEY = 'Access-Control-Allow-Origin'

    def __init__(self, configuration: Configuration) -> None:

        assert isinstance(configuration, Configuration)
        self._configuration = configuration

        return

    allowed_origin = Immutable(lambda s: s._compute_allowed_origin())

    def _compute_allowed_origin(self) -> str:
        """Return the string origin that is allowed to make requests"""
        if self._configuration.disable_cors_restrictions is True:
            return self._ALL_ORIGINS
        if self._configuration.debug is True:
            return self._configuration.local_origin
        return self._configuration.restricted_origin

    def apply_to_headers(self, headers: Headers) -> Headers:
        """Return Headers with CORS policy applied"""
        headers.add(
            self._HEADER_KEY,
            self.allowed_origin
        )
        return headers
