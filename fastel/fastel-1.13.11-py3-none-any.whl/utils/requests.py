from functools import wraps
from typing import Any, Callable, TypeVar, cast

import requests as _requests

FuncT = TypeVar("FuncT", bound=Callable[..., Any])
WrapT = TypeVar("WrapT", bound=Callable[..., Any])


def log_all(action: str) -> WrapT:
    def inner(fn: FuncT) -> FuncT:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            url: str = args[0]
            json = kwargs.get("json", None)
            print("[REQ]", action, url, json)
            return fn(*args, **kwargs)

        return cast(FuncT, wrapper)

    return cast(WrapT, inner)


@log_all("get")  # type: ignore
def get(*args: Any, **kwargs: Any) -> Any:
    return _requests.get(*args, **kwargs)


@log_all("post")  # type: ignore
def post(*args: Any, **kwargs: Any) -> Any:
    return _requests.post(*args, **kwargs)


@log_all("put")  # type: ignore
def put(*args: Any, **kwargs: Any) -> Any:
    return _requests.put(*args, **kwargs)


@log_all("delete")  # type: ignore
def delete(*args: Any, **kwargs: Any) -> Any:
    return _requests.delete(*args, **kwargs)
