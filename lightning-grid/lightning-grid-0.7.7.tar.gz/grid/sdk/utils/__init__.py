from contextlib import contextmanager
import os
from pathlib import Path
from typing import Any

from grid.sdk.utilities import SPECIAL_NAME_TO_SKIP_OBJECT_INIT


@contextmanager
def current_working_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def fill_object_from_response(obj: Any, response: Any) -> Any:
    """Fill the given object with the REST response using the object
    method `_setup_from_response`
    """
    obj._setup_from_response(response)  # noqa
    return obj
