class DomainBaseException(Exception):
    def __init__(self, message=None, title=None, code=None):
        self.message = message
        self.code = code
        self.title = title
        super().__init__(self.message)


class DomainException(DomainBaseException):
    def __init__(self, message=None, title='Domain Exception', code=None):
        super().__init__(message, title, code)


class EntityNotFound(DomainBaseException):
    def __init__(self, message=None, title='Entity Not Found', code=None):
        super().__init__(message, title, code)
