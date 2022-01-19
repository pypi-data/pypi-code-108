from __future__ import annotations

from typing import Any, Callable, Literal


def TAUTOLOGY(*args: Any, **kwargs: Any) -> Literal[True]:
    return True


def CONTRADICTION(*args: Any, **kwargs: Any) -> Literal[False]:
    return False


def VOID(*args: Any, **kwargs: Any) -> None:
    pass


async def ASYNC_VOID(*args: Any, **kwargs: Any) -> None:
    pass


def TAUTOLOGY_FACTORY() -> Callable[..., Literal[True]]:
    return TAUTOLOGY


def NOOP() -> None:
    return None


async def ASYNC_NOOP() -> None:
    return None


def RETURN_TRUE() -> Literal[True]:
    return True


def RETURN_FALSE() -> Literal[False]:
    return False
