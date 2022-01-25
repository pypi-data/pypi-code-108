class MException(Exception):
    """Custom JSON based exception.

    :param code: response code
    :param message: exception message
    """
    message = ''

    def __init__(self, code=None, message=None):
        Exception.__init__(self)
        if message is not None:
            self.message = message

        if code is not None:
            self.code = code

    def to_dict(self):
        return {
            'code': self.code,
            'desc': self.message
            # 'type': str(self.__class__.__name__)
        }


class InvalidRequestType(MException):
    """
    Raised when an invalid Request-Type is provided.
    """
    pass
