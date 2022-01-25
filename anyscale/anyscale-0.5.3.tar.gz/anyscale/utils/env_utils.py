import contextlib
import os
from typing import Any, Generator


@contextlib.contextmanager
def set_env(**environ: Any) -> Generator[None, None, None]:
    """
    Temporarily set the process environment variables.
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)
