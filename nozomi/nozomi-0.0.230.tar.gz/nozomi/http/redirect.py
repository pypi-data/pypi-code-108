"""
Nozomi
Redirect Module
author: hugh@blinkybeach.com
"""
from nozomi.http.url_parameter import URLParameter
from nozomi.http.url_parameters import URLParameters
from nozomi.http.query_string import QueryString
from typing import TypeVar, Type, Optional, Union, List

T = TypeVar('T', bound='Redirect')


class Redirect(Exception):
    """
    An exception in program flow that requires the user to be redirected.
    """
    def __init__(
        self,
        destination: str,
        allow_next: bool = True,
        preserve_arguments: bool = True,
        extra_parameters: List[URLParameter] = list()
    ) -> None:

        assert isinstance(destination, str)
        assert isinstance(allow_next, bool)
        self._destination = destination
        self._allow_next = allow_next
        self._preserve_arguments = preserve_arguments
        self._base_parameters = extra_parameters

        return

    def destination(
        self,
        next_url: Optional[str] = None,
        query_string: bytes = b''
    ) -> str:
        """
        Return an application path to which a user should be
        redirected
        """
        destination = self._destination
        base_parameters = self._base_parameters

        if next_url is not None and self._allow_next is True:
            assert isinstance(next_url, str)
            base_parameters = self.strip_next(query=base_parameters).parameters
            base_parameters.append(URLParameter('then', next_url))

        if self._preserve_arguments is False:
            parameters = URLParameters(base_parameters)
            return parameters.add_to(destination)

        raw_query_string = query_string.decode()
        existing_keys = [p.key for p in base_parameters]
        elements = raw_query_string.split('&')
        for element in elements:
            if len(element) < 1:
                continue
            if element[0] == '?':
                element = element[1:]
            pieces = element.split('=')
            assert len(pieces) == 2
            key = pieces[0]
            value = pieces[1]
            if key in existing_keys:
                continue
            base_parameters.append(URLParameter(key, value))
            continue

        parameters = URLParameters(base_parameters)

        return parameters.add_to(destination)

    @classmethod
    def strip_next(
        cls: Type[T],
        query: Optional[Union[bytes, QueryString, List[URLParameters]]]
    ) -> URLParameters:
        """
        Return a query string, of type string, stripped of all "then"
        arguments
        """

        parameters: List[URLParameter] = list()

        if query is None:
            return URLParameters(parameters)

        if isinstance(query, list):
            assert False not in [isinstance(q, URLParameter) for q in query]
            stripped_targets: List[URLParameter] = list()
            for target in query:
                if target.key == 'then':
                    continue
                stripped_targets.append(target)
                continue
            return URLParameters(stripped_targets)

        if isinstance(query, QueryString):

            for key in query:
                if key == 'then':
                    continue
                parameters.append(URLParameter(key, query[key]))
                continue
            return URLParameters(parameters)

        if isinstance(query, bytes):
            query_string = query.decode()
            elements = query_string.split('&')
            for element in elements:
                if len(element) < 1:
                    continue
                if element[0] == '?':
                    element = element[1:]
                pieces = element.split('=')
                assert len(pieces) == 2
                if pieces[0] == 'then':
                    continue
                parameters.append(URLParameter(pieces[0], pieces[1]))
                continue
            return URLParameters(parameters)

        raise TypeError('query must be `bytes` or `QueryString`')

    @classmethod
    def to_next_path(
        cls: Type[T],
        query: Optional[QueryString],
        fallback_to_path: str,
        preserve_arguments: bool = False,
        extra_parameters: List[URLParameters] = list()
    ) -> None:

        arguments = ''
        if preserve_arguments is True and query is not None:
            arguments = cls.strip_next(query).query_string

        next_path = None
        if query is not None:
            next_path = query.optionally_parse_string('then', max_length=96)
        if next_path is None:
            next_path = fallback_to_path

        raise cls(
            destination=next_path,
            allow_next=False,
            preserve_arguments=True,
            extra_parameters=extra_parameters
        )
