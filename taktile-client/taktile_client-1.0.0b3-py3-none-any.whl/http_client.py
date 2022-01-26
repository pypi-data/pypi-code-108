"""
General HTTP Client with Pydantic support
"""
import logging
import typing as t

import requests
from pydantic import BaseModel

from taktile_client.config import settings, version

logger = logging.getLogger(__name__)

API_KEY_HEADER = "X-Api-Key"


class API:
    """API.
    Basic HTTP client with support for model parsing
    """

    def __init__(
        self,
        api_base: str,
        api_key: t.Optional[str],
        headers: t.Optional[t.Dict[str, str]] = None,
    ):
        self._base = api_base
        self.set_headers(headers)
        self.set_api_key(api_key)

    def set_headers(self, headers: t.Optional[t.Dict[str, str]]) -> None:
        """set_headers.
        Sets headers. If specified it will override the base headers, if not
        it will use the base headers.

        Parameters
        ----------
        headers: t.Optional[t.Dict[str, str]]
            headers to merge
        """
        base_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"taktile-client/{version}",
        }
        if headers:
            self._headers = {**base_headers, **headers}
        else:
            self._headers = base_headers

    def set_api_key(self, api_key: t.Optional[str]) -> None:
        """set_api_key.
        Sets api key header. If specified will use the specified one.  If not
        specified, will use one that is specified in the environment.
        Parameters
        ----------
        api_key : t.Optional[str]
            api_key to be set
        """
        if api_key is None:
            api_key = settings.TAKTILE_API_KEY
        if api_key is None:
            self._headers = {
                k: v for (k, v) in self._headers.items() if k != API_KEY_HEADER
            }
        else:
            self._headers = {**self._headers, **{API_KEY_HEADER: api_key}}

    def call(
        self,
        *,
        verb: str,
        path: str,
        model: t.Optional[t.Type[BaseModel]] = None,
        raw: bool = False,
        **kwargs: t.Any,
    ) -> t.Any:
        """
        Call an endpoint

        Parameters
        ----------
        verb : str
            verb to use
        path : str
            path to call
        model : t.Optional[t.Type[BaseModel]]
            model to parse the response into
        raw : bool
            if true, return the unparsed response
        kwargs :
            kwargs passed on to requests.<verb>()
        """
        path = requests.compat.urljoin(self._base, path)  # type: ignore
        logger.debug("%s %s: %s", verb, path, str(kwargs))
        response = getattr(requests, verb)(
            path, **kwargs, headers=self._headers
        )

        if raw:
            return response

        if not response.ok:
            logger.error(
                "%s %s: %s - %s - %s",
                verb,
                path,
                str(kwargs),
                response.status_code,
                response.content,
            )
            response.raise_for_status()

        logger.info(
            "%s %s: %s - %s - %s",
            verb,
            path,
            str(kwargs),
            response.status_code,
            response.content,
        )

        json = response.json()

        if model is None:
            return json

        if isinstance(json, list):
            return [model(**x) for x in json]

        return model(**json)
