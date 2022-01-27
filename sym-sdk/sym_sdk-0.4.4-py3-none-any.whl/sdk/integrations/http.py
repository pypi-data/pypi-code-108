"""The HTTP Integration allows arbitrary HTTP requests to be made to remote servers.

The API is similar to that of the :mod:`~requests` library.
"""

from typing import Dict, Literal, Optional, Union

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


def request(url: str, method: HTTPMethod, body: Optional[Dict] = None):
    """Makes an HTTP request to the given URL with the specified method and body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """


def get(url: str) -> Union[str, dict]:
    """Makes a GET request to the given URL.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """


def post(url: str, body: Optional[Dict] = None) -> Union[str, dict]:
    """Makes a POST request to the given URL, with the specified body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """


def put(url: str, body: Optional[Dict] = None) -> Union[str, dict]:
    """Makes a PUT request to the given URL, with the specified body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """


def patch(url: str, body: Optional[Dict] = None) -> Union[str, dict]:
    """Makes a PATCH request to the given URL, with the specified body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """


def delete(url: str, body: Optional[Dict] = None) -> Union[str, dict]:
    """Makes a DELETE request to the given URL, with the specified body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """
