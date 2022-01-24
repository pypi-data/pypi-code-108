from nehushtan.httpd.exceptions.NehushtanHTTPError import NehushtanHTTPError


class NehushtanRequestParameterError(NehushtanHTTPError):
    """
    When a request cannot be processed due to errors in the parameters
    """

    TYPE_QUERY = "QUERY"
    TYPE_BODY = "BODY"
    TYPE_HEADER = "HEADER"
    TYPE_COOKIE = "COOKIE"

    DESC_NOT_SET = 'NOT_SET'
    DESC_FORMAT_ERROR = "FORMAT_ERROR"

    def __init__(self, key: str, key_type: str, desc: str = 'Undetermined Error', http_code: int = 400):
        super().__init__(
            f'Request Key [{key}] of Type [{key_type}]: {desc}',
            http_code
        )
        self.key = key
        self.key_type = key_type
        self.desc = desc
