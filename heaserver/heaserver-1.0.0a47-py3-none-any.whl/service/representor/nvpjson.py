"""
Name-value-pair (NVP) JSON representor. It just serializes a run-time WeSTL document's data section verbatim.
"""

from heaobject.root import json_dumps
from .error import ParseException
from .representor import Representor, Link
from ..jsonschemavalidator import NVPJSON_SCHEMA_VALIDATOR, ValidationError
from aiohttp.web import Request
from typing import Any, Union, Dict, List, Callable
from itertools import chain


MIME_TYPE = 'application/json'


class NVPJSON(Representor):
    MIME_TYPE = MIME_TYPE

    async def formats(self, request: Request,
                      wstl_obj: Union[List[Dict[str, Any]], Dict[str, Any]],
                      dumps=json_dumps,
                      link_callback: Callable[[int, Link], None] = None) -> bytes:
        """
        Formats a run-time WeSTL document as a list of name-value pair JSON documents.

        :param request: the HTTP request.
        :param wstl_obj: dict with run-time WeSTL JSON, or a list of run-time WeSTL JSON dicts.
        :param dumps: any callable that accepts dict with JSON and outputs str. Cannot be None.
        :param link_callback: ignored.
        :return: JSON string.
        """
        if not isinstance(wstl_obj, list):
            wstl_obj_ = wstl_obj['wstl'].get('data', [])
        else:
            wstl_obj_ = list(chain.from_iterable(w['wstl'].get('data', []) for w in wstl_obj))
        return dumps(wstl_obj_).encode('utf-8')

    async def parse(self, request: Request) -> Dict[str, Any]:
        """
        Parses the body of an HTTP request containing a JSON document into a dict-like object.

        :param request: the HTTP request. Cannot be None.
        :return: the data section of the JSON document transformed into a dict.
        """
        try:
            result = await request.json()
        except ValueError as e:
            raise ParseException from e
        try:
            NVPJSON_SCHEMA_VALIDATOR.validate(result)
            return result
        except ValidationError as e:
            raise ParseException from e


