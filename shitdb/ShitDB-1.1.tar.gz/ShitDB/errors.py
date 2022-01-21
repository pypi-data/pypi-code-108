"""
Just to keep the library clean and structured
"""



class ShitException(Exception):
    pass


class BadArgs(ShitException):
    pass


class NotFound(ShitException):
    pass


class Forbidden(ShitException):
    pass



class ServiceUnavailable(ShitException):
    pass


class RateLimited(ShitException):
    pass


class Unauthorized(ShitException):
    pass
