# __all__ = [
#     # warnings
#     # exceptions
#     'TmeCmsException',
#     'NeedLoginException',
# ]


class TmeCmsException(Exception):
    pass


class NeedLoginException(TmeCmsException):
    def __init__(self, what):
        """
        使用某方法需要登录而当前客户端未登录

        :param str|unicode what: 当前试图调用的方法名
        """
        self.what = what

    def __repr__(self):
        return '需要登录才能使用 [{self.what}] 方法。'.format(self=self)

    __str__ = __repr__


class LoginError(TmeCmsException):
    """
    所有登录中发生的错误
    """
