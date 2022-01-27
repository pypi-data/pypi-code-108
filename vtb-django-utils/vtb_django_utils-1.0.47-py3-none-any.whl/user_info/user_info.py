import contextvars

_user_info = contextvars.ContextVar('user_info', default={})


def get_user_info():
    return _user_info.get() or {}


def set_user_info(value):
    return _user_info.set(value)
