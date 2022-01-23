"""
Nozomi
URL Parameters Module
author: hugh@blinkybeach.com
"""
from nozomi.ancillary.immutable import Immutable
from nozomi.http.url_parameter import URLParameter
from typing import List, TypeVar

T = TypeVar('T', bound='URLParameters')


class URLParameters:
    """A collection of URL path paraemeters"""

    def __init__(self, targets: List[URLParameter]) -> None:

        assert isinstance(targets, list)
        assert False not in [isinstance(t, URLParameter) for t in targets]

        self._targets = targets
        return

    query_string = Immutable(lambda s: s._form_query_string())
    parameters: List[URLParameter] = Immutable(lambda s: s._targets)

    def _form_query_string(self) -> str:
        if len(self._targets) < 1:
            return ''

        query = '?' + str(self._targets[0])

        for target in self._targets[1:]:
            query += '&' + str(target)

        return query

    def add_to(self, url: str) -> str:
        """Return a URL with parameters bolted on"""
        if len(self._targets) < 1:
            return url

        return url + self.query_string


QueryParameters = URLParameters
