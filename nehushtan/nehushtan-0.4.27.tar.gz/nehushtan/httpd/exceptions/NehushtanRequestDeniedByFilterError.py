from nehushtan.httpd.exceptions.NehushtanHTTPError import NehushtanHTTPError


class NehushtanRequestDeniedByFilterError(NehushtanHTTPError):
    """
    Since 0.4.0
    When a Filter denies a request
    """

    def __init__(self, filter_name: str, error_message: str, http_code: int):
        super(NehushtanRequestDeniedByFilterError, self).__init__(
            f'Filter [{filter_name}] Denied Request: {error_message}',
            http_code
        )
