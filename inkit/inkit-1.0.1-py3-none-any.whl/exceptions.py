class InkitException(Exception):
    """
    Base exception. It may contain `message`, `exc` and `response` attributes for
    exception representation.
    """
    def __init__(self, message=None, resp=None, exc=None):
        self._message = message
        self.response = resp
        self.exc = exc

        if not self._message and self.exc:
            self._message = str(self.exc)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self._message}"

    @property
    def message(self):
        msg = self._message
        if self.response:
            msg = f'{msg}, code {self.response.status_code}'
        return msg


class InkitRouterException(InkitException):
    """Raises when Router failed"""
    pass


class InkitClientException(InkitException):
    """Raises when Client failed"""
    pass


class InkitResponseException(InkitClientException):
    """Raises when API response has aт unsuccessful status code"""
    pass
