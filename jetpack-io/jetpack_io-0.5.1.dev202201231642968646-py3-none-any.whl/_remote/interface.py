import functools
from typing import Any, Callable

from jetpack import _remote

SERVER = _remote.server.Server()
CLIENT = _remote.client.Client()


def remote(fn: Callable[..., Any]) -> Callable[..., Any]:  # Decorator
    symbol = export(fn)
    stub = remote_function(symbol)
    return functools.wraps(fn)(stub)


def export(fn: Callable[..., Any]) -> str:
    return SERVER.export(fn)


def remote_function(symbol: str) -> Callable[..., Any]:
    return CLIENT.remote_function(symbol)
