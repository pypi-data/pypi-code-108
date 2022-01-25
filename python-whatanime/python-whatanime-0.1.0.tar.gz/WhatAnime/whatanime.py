from typing import IO, Any, Dict
import requests
from WhatAnime import exception as error

class Client:
    """"[summary]

    :param token: [description]
    :type token: str
    :param image: [description]
    :type image: IO
    :param host: [description], defaults to "https://trace.moe/api/search"
    :type host: str, optional
    """

    def __init__(self, token: str, image: IO | str, host: str = "https://trace.moe/api/search") -> None:
        self._host = host
        self._sesion = requests.Session()
        self._sesion.headers.update({"x-trace-key": f"[{token}]"})


    def _make_request(self, path: str, method: str = "get", **kwargs: Dict[Any, Any]) -> None:
        """
        Make a reuqest and handle errors

        Args:
            `path`: Path on the API without `/`
            `method`: The HTTP request method, defaults to GET
            `**kwargs`: Keyword arguments to the request method.

        Returns: The json response and the request object.
        """