"""
Nozomi
Server Name Class
author: hugh@blinkybeach.com
"""
from nozomi.ancillary.configuration import Configuration
from nozomi.http.headers import Headers


class ServerName:

    def __init__(self, configuration: Configuration):

        self._configuration = configuration
        return

    def apply_to_headers(self, headers: Headers) -> Headers:
        """Apply server name to headers and return them"""
        headers.add('Server', self._configuration.server_name)
        return headers
