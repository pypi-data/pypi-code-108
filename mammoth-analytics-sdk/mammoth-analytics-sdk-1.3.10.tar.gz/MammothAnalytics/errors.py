from __future__ import unicode_literals
import logging

log = logging.getLogger(__name__)


class ErrorObject():
    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message

    def get_message(self):
        return self.message

    def get_as_dict(self):
        return {
            'ERROR_CODE': self.code,
            'ERROR_MESSAGE': self.message
        }


class MammothException(Exception):
    def __init__(self, code, message):
        self.error_object = ErrorObject(code, message)
        super(MammothException, self).__init__(self.error_object.get_message())


class AuthError(MammothException):
    pass


class UnknownError(MammothException):
    pass


class NotFoundError(MammothException):
    pass


class AuthenticationError(MammothException):
    pass


class AuthorizationError(MammothException):
    pass


class MalformedRequestError(MammothException):
    pass
