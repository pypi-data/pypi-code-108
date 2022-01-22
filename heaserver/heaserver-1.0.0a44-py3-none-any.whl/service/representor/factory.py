"""
A factory for getting a representor object from the heaserver.service.representor package for a provided mimetype. A
representor formats WeSTL documents into one of various output formats, and it may provide for parsing data represented
in the format into name-value pair (NVP) JSON. Supported mimetypes are application/vnd.wstl+json (WeSTL),
application/json (name-value pair JSON), and application/vnd.collection+json (Collection+JSON).
"""
from . import wstljson, nvpjson, cj, xwwwformurlencoded, representor
from accept_types import get_best_match
from typing import Optional, Mapping, Type
from enum import Enum


# Priority-ordered mapping of mime types to representor implementation. The priority ordering is used by
# get_from_accepts_header() to select a representor when multiple candidate mime types are found in the Accepts header.
# Python dicts have guaranteed insertion order since version 3.7.
_mime_type_to_representor: Mapping[str, Type[representor.Representor]] = {
    cj.MIME_TYPE: cj.CJ,
    wstljson.MIME_TYPE: wstljson.WeSTLJSON,
    nvpjson.MIME_TYPE: nvpjson.NVPJSON,
    xwwwformurlencoded.MIME_TYPE: xwwwformurlencoded.XWWWFormURLEncoded
}


DEFAULT_REPRESENTOR = cj.CJ


class AcceptHeaderFilter(Enum):
    ANY = 1
    SUPPORTS_LINKS = 2


def from_accept_header(accept: Optional[str], accept_header_filter: Optional[AcceptHeaderFilter] = None) -> Optional[representor.Representor]:
    """
    Selects a representor from the contents of a HTTP Accept header.

    :param accept: an Accept header string.
    :param accept_header_filter: whether to consider only representors that support HTML links. None is equivalent to
    AcceptsHeaderFilter.ANY.
    :return: An object that implements the representor interface, described in the heaserver.service.representor
    package documentation. It will return a representor for Collection+JSON if the provided mimetype is None.
    If the Accept header doesn't match any of the support response content types, None will be returned.
    """
    def predicate(representor_: Type[representor.Representor]):
        if accept_header_filter in (None, AcceptHeaderFilter.ANY):
            return True
        if accept_header_filter == AcceptHeaderFilter.SUPPORTS_LINKS and representor_.supports_links():
            return True
        return False
    if accept is None:
        return DEFAULT_REPRESENTOR() if predicate(DEFAULT_REPRESENTOR) else None
    result = get_best_match(accept.lower(), (k for k, v in _mime_type_to_representor.items() if predicate(v)))
    if result is None:
        return None
    else:
        return _mime_type_to_representor[result]()


def from_content_type_header(content_type: Optional[str]) -> representor.Representor:
    """
    Selects a representor from the contents of a HTTP Content-Type header.

    :param content_type: the Content-Type header string.
    :return: An object that implements the representor interface, described in the heaserver.service.representor
    package documentation. It will return a representor for Collection+JSON if the provided mimetype is None or unknown.
    """
    if not content_type:
        return DEFAULT_REPRESENTOR()
    return _mime_type_to_representor.get(content_type.split(';')[0].strip().lower(), DEFAULT_REPRESENTOR)()
