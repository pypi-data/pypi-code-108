from typing import Dict, Any, Optional
from urllib.parse import urlencode
import urllib.parse as urlparse


def url_append(
    url: str,
    query_extra: Optional[Dict[str, Any]] = None,
    path_extra: Optional[str] = None,
) -> str:
    """
    Provided an URL, this function adds (or overwrites) one or more
    query parameters and/or path, and returns the updated URL.

    :param url: The URL to add query parameters to
    :param query_extra: The query parameters to add
    :param path_extra: The path to add
    :return: The URL with added query parameters
    """
    url_parts = list(urlparse.urlparse(url))

    if path_extra is not None:
        url_parts[2] += path_extra

    if query_extra is not None:
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(query_extra)
        url_parts[4] = urlencode(query)

    return urlparse.urlunparse(url_parts)
