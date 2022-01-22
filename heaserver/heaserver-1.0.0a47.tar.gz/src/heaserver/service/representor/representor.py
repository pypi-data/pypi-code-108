from yarl import URL
from aiohttp.web import Request
from typing import Union, Any, Dict, List, Sequence, Callable, Optional
import abc
from dataclasses import dataclass
from heaobject.root import json_dumps


@dataclass
class Link:
    """
    Represents a Link for the link_callback callback that may be passed into the Representor.formats method.
    """
    href: Union[URL, str]
    rel: Sequence[str]
    prompt: Optional[str] = None


class Representor(abc.ABC):
    """
    Abstract base class for formatting WeSTL documents into a response body and parsing an HTTP request body into a
    name-value pair JSON dict.
    """
    MIME_TYPE: str = ''

    @classmethod
    def supports_links(cls) -> bool:
        """
        The default implementation returns False to indicate that the representor does not support HTML links.
        Subclasses should override this method to return True.

        :return: False
        """
        return False

    @abc.abstractmethod
    async def formats(self, request: Request,
                      wstl_obj: Union[List[Dict[str, Any]], Dict[str, Any]],
                      dumps=json_dumps,
                      link_callback: Callable[[int, Link], None] = None) -> bytes:
        """
        Formats a run-time WeSTL document into a response body.

        :param request: the HTTP request.
        :param wstl_obj: dict with run-time WeSTL JSON, or a list of run-time WeSTL JSON dicts.
        :param dumps: any callable that accepts dict with JSON and outputs str. Cannot be None. By default, it uses
        the heaobject.root.json_dumps function, which dumps HEAObjects and their attributes to JSON objects. Cannot
        be None.
        :param link_callback: a callable that will be invoked whenever a link is created from a WeSTL action in the
        wstl_obj. Links can be specific to a data item in the wstl_obj's data list or "global" to the entire data list.
        The first parameter contains the index of the data item, or None if the link is global. The second
        parameter contains the link as a heaserver.service.representor.Link object. The purpose of this
        callback is to access parameterized links after their parameters have been filled in.
        :return: a bytes object containing the formatted data.
        """
        pass

    @abc.abstractmethod
    async def parse(self, request: Request) -> Dict[str, Any]:
        """
        Parses an HTTP request body into a name-value pair dict-like object.

        :param request: the HTTP request. Cannot be None.
        :return: a dict.
        """
        pass

