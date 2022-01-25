# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import urllib.parse as urllib

from typing import List, Optional


class UriBuilder:
    """
    Builds a URI, taking care of URI escaping and ensuring a well-formatted URI.
    """

    def __init__(
        self,
        scheme: Optional[str] = None,
        hostname: Optional[str] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
        rstrip_slash: bool = True,
    ):
        # Port is not allowed without a hostname
        assert (port and hostname) or (not hostname)

        self._scheme = scheme
        self._hostname = hostname
        self._port = port
        self._path = path or ''
        if rstrip_slash:
            self._path = self._path.rstrip('/')
            if not self._path.startswith('/'):
                self._path = '/' + self._path
        self._query_params: List[str] = []
        self._fragment = ''

    def add_path_component(self, component: str, append_slash: bool = False) -> 'UriBuilder':
        """
        Adds a single path component to the URI. Any characters not in the
        unreserved set, including '/', will be escaped.
        """
        # Completely URI encode the component, even the '/' characters
        self._path = '{}/{}'.format(self._path, urllib.quote(component, ''))
        if append_slash:
            self.append_slash()
        return self

    def append_slash(self) -> 'UriBuilder':
        self._path += '/'
        return self

    def add_query_param(self, name: str, value: Optional[object] = None) -> 'UriBuilder':
        """
        Adds a query parameter with an optional value to the query string. Any
        characters not in the reserved set will be escaped. Spaces will be
        escaped with '+' characters
        """
        if value is not None:
            self._query_params.append(
                '{}={}'.format(urllib.quote(name, ''), urllib.quote(str(value), ''))
            )
        else:
            self._query_params.append(urllib.quote_plus(name))

        return self

    def __str__(self) -> str:
        # Consider an empty path to be the root for string-printing purposes
        path = '/' if not self._path else str(self._path)
        scheme = '' if not self._scheme else self._scheme
        netloc = '' if not self._netloc() else self._netloc()
        params = '&'.join(self._query_params)
        return urllib.urlunsplit((scheme, netloc, path, params, None))

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def _netloc(self) -> str:
        netloc = ''
        if self._hostname:
            if self._port:
                port_part = ':%s' % str(self._port)
            else:
                port_part = ''
            netloc += f'{self._hostname}{port_part}'

        return netloc
