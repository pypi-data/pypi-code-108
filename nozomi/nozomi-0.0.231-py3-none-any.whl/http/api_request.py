"""
Nozomi
API Request Module
author: hugh@blinkybeach.com
"""
from nozomi.http.method import HTTPMethod
from nozomi.ancillary.configuration import Configuration
from nozomi.ancillary.immutable import Immutable
from nozomi.http.url_parameters import URLParameters
from urllib.request import Request
from urllib.request import urlopen
from typing import Any, Optional, TypeVar, Dict
from urllib.request import HTTPError
import json
from nozomi.security.request_credentials import RequestCredentials

T = TypeVar('T', bound='ApiRequest')


class ApiRequest:
    """A request to a Nozomi-compliant API via HTTP"""

    def __init__(
        self,
        path: str,
        method: HTTPMethod,
        configuration: Configuration,
        data: Optional[Any] = None,
        url_parameters: Optional[URLParameters] = None,
        credentials: Optional[RequestCredentials] = None
    ) -> None:

        url = configuration.api_endpoint + path
        if url_parameters is not None:
            url = url_parameters.add_to(url)

        headers: Dict[str, str] = dict()
        if credentials is not None:
            headers = credentials.dictionary

        if data is not None:
            data = json.dumps(data).encode('utf-8')
            headers['content-type'] = 'application/json'

        request = Request(
            url,
            method=method.value,
            data=data,
            headers=headers
        )

        try:
            response = urlopen(request).read()
        except HTTPError as error:
            if error.code == 404:
                self._response_data = None
                return
            raise

        self._response_data = json.loads(response)

        return

    response_data = Immutable(lambda s: s._response_data)
