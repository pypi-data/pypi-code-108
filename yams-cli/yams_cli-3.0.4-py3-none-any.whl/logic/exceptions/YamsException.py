class BaseException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value


class ConflictException(BaseException):
    def __init__(self, message):
        super().__init__(message)


class NotFoundException(BaseException):
    def __init__(self, message):
        super().__init__(message)


class InvalidInputException(BaseException):
    def __init__(self, message):
        super().__init__(message)


class UnauthorizedException(BaseException):
    def __init__(self, message):
        super().__init__(message)


class ErrorException(BaseException):
    def __init__(self, message):
        super().__init__(message)
