from nehushtan.httpd.exceptions.NehushtanHTTPError import NehushtanHTTPError


class NehushtanRequestProcessTargetError(NehushtanHTTPError):
    """
    Since 0.4.0
    When the process target of the matched Route (filters or controllers) does not work
    """
    pass
