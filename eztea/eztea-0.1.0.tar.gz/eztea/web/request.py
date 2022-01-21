import cgi

import falcon
from validr import T, modelclass

__all__ = (
    "MIME_TYPE_JSON",
    "MIME_TYPE_MULTIPART",
    "MIME_TYPE_URLENCODED",
    "MIME_TYPE_TEXT",
    "parse_content_type",
    "Request",
    "FormFile",
)

MIME_TYPE_JSON = "application/json"
MIME_TYPE_MULTIPART = "multipart/form-data"
MIME_TYPE_URLENCODED = "application/x-www-form-urlencoded"
MIME_TYPE_TEXT = "text/plain"


def parse_content_type(content_type: str):
    if not content_type:
        return ("", {})
    mimetype, params = cgi.parse_header(content_type)
    return mimetype.lower(), params


class Request(falcon.Request):
    @property  # TODO: remove py37 and use cached_property
    def __content_type_parsed(self):
        return parse_content_type(self.content_type)

    @property
    def mimetype(self):
        """
        Like content_type, but without parameters (eg, without charset,
        type etc.) and always lowercase. For example if the content type is
        text/HTML; charset=utf-8 the mimetype would be 'text/html'.
        """
        return self.__content_type_parsed[0]

    @property
    def mimetype_params(self):
        """
        The mimetype parameters as dict. For example if the content type is
        text/html; charset=utf-8 the params would be {'charset': 'utf-8'}.
        """
        return self.__content_type_parsed[1]


@modelclass
class FormFile:
    # content type
    content_type: str = T.str
    # secure filename
    filename: str = T.str
    # file data
    data: bytes = T.bytes
