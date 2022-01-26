from typing import Callable

from spell.serving.predictor import Endpoint


def with_background_tasks(name: str = "tasks") -> Callable:
    def decorator(f):
        if not hasattr(f, "__injected_params__"):
            f.__injected_params__ = Endpoint(f, tasks=name)
        else:
            f.__injected_params__.tasks = name
        return f

    return decorator


def with_full_request(name: str = "request") -> Callable:
    def decorator(f):
        if not hasattr(f, "__injected_params__"):
            f.__injected_params__ = Endpoint(f, request=name)
        else:
            f.__injected_params__.request = name
        return f

    return decorator
