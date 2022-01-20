from functools import wraps

from jnt_django_toolbox.context_managers import global_lock


def one_at_time(func):
    """Ensures that function runned only one at time."""

    @wraps(func)
    def handle(*args, **kwargs):  # noqa:  WPS110
        with global_lock(func.__name__) as acquired:
            if acquired:
                return func(*args, **kwargs)

    return handle
