from pathlib import Path
from contextlib import contextmanager
import os

@contextmanager
def cd(path):
    """Sets the cwd within the context
    """
    origin = Path().resolve()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)

