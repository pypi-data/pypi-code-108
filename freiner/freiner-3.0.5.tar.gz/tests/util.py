import functools
import math
import time
from pathlib import Path
from typing import Any, Callable, ContextManager, cast

from freezegun import freeze_time as _freeze_time
from freezegun.api import FrozenDateTimeFactory


ROOTDIR = Path(__file__).parent.parent
DOCKERDIR = ROOTDIR / ".docker"


def fixed_start(func: Callable[..., Any]):
    @functools.wraps(func)
    def _inner(*args: Any, **kwargs: Any):
        start = time.time()
        while time.time() < math.ceil(start):
            time.sleep(0.01)
        return func(*args, **kwargs)

    return _inner


def freeze_time() -> ContextManager[FrozenDateTimeFactory]:
    f = _freeze_time()
    # This is a necessary fix for our testing, and the third-party type hints aren't sufficient
    f.ignore = tuple(set(f.ignore) - {"threading"})  # type: ignore
    # mypy can't handle the fact that I'm narrowing the return type on purpose, so this has to be casted manually
    return cast(ContextManager[FrozenDateTimeFactory], f)
