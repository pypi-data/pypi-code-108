# coding: utf-8
import re
from six.moves import urllib


def add_query(url, **query):
    """Adds query parameters to a URL

    >>> add_url_arguments("http://google.com", q="what is glibs")
    "http://google.com?q=what+is+glibs"
    """
    url_parts = list(urllib.parse.urlparse(url))
    query = urllib.parse.parse_qsl(url_parts[4]) + list(query.items())
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    return urllib.parse.urlunparse(url_parts)


def is_valid(url):
    if len(url) > 2048:  # pragma: no cover
        return False

    regex = (
        r"^(https?://)?"  # protocol
        r"((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,})"  # domain name
        r"(:\d+)?(/[-;&a-zçãºª\d()\[\]{}%_.,~+!:@=*$?]*)*"  # port and path
        r"(\?[-;&a-zçãºª\d()[]{}%_.~+=!:,]*)?"  # query string
        r"(#.*)?$"  # fragment locator
    )

    p = re.compile(regex, re.IGNORECASE)

    return bool(re.search(p, url))


# Alias for backward compatibility
add_url_arguments = add_query
is_valid_url = is_valid
