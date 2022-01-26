import asyncio
from functools import wraps
import importlib
from logging import Logger
import os
from pathlib import Path
import sys
from typing import Awaitable, Callable, Optional, Tuple, Union

from aiohttp import ClientConnectionError, ClientResponse

from spell.serving.exceptions import InvalidPredictor

# This makes the max wait 960ms
RETRY_ATTEMPTS = 5
RETRY_BASE_WAIT_MS = 60


def import_user_module(
    module_path: Optional[Union[Path, str]],
    python_path: str,
):
    # module_path is the path in the filesystem to the module
    # python_path is the python path to the predictor in the form path.to.module
    validate_python_path(python_path)
    if module_path:
        sys.path.append(str(module_path))  # Path objects can't be used here
    importlib.import_module(python_path)


def validate_python_path(python_path: str):
    split_python_path = python_path.split(".")
    if split_python_path[0] == "spell":
        raise InvalidPredictor('Top-level module for predictor cannot be named "spell"')
    invalid_path_identifier = next(
        (identifier for identifier in split_python_path if not identifier.isidentifier()), None
    )
    if invalid_path_identifier:
        raise InvalidPredictor(f"Invalid python path element {invalid_path_identifier}")


def retry(url: str, logger: Logger) -> Callable:
    """An async exponential backoff decorator"""

    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs) -> Awaitable[ClientResponse]:
            num_attempts = 0
            error = None
            while num_attempts <= RETRY_ATTEMPTS:
                try:
                    return await f(*args, **kwargs)
                except ClientConnectionError as e:
                    num_attempts += 1
                    error = e
                    msg = f"Got error {e} on {url} on attempt {num_attempts}."
                    if num_attempts < RETRY_ATTEMPTS:
                        wait_time = RETRY_BASE_WAIT_MS * 2 ** num_attempts
                        logger.warning(f"{msg} Retrying in {wait_time}ms...")
                        await asyncio.sleep(wait_time / 1000)
                    else:
                        logger.error(msg)
                        break
            raise error

        return wrapper

    return decorator


def path_to_pypath(path: str) -> str:
    pypath = path.lstrip(os.path.sep)
    if pypath[-3:] != ".py":
        raise InvalidPredictor("Predictor must be in a Python file")
    pypath = pypath[:-3]
    return pypath.replace(os.path.sep, ".")


def strip_path_prefix(path: Path, prefix: Path) -> str:
    suffix = str(path)
    if prefix != Path("."):
        suffix = suffix[len(str(prefix)) :]
    return suffix


def get_module_path_and_python_path(path: Path, root: Path) -> Tuple[Optional[Path], str]:
    """Split a path to a module and python path so it can be imported programatically
    Provided a file to import, we traverse up the directory structure until we find a directory
    without an __init__.py file. This will be used as the module path, and will later be appended
    to sys.path. The path from this directory to the specified file is converted into a Python path
    by stripping the ".py" file extension and replacing the "/"'s with "."'s. The result is a tuple
    of a path relative to the repo root to the directory of the python module and a python path to
    the file within that module.
    """
    # Traverse up the the directory structure from the specified file until we find a directory
    # Which does not contain an __init__.py, indicating it's not a Python module, or we reach root
    # Indicating the root of the repo is a Python module.
    module_path = None
    for parent in path.parents:
        if parent == root:
            break
        if "__init__.py" not in {p.parts[-1] for p in parent.iterdir()}:
            module_path = parent
            break
    # Extract the path from the module/root to the Python file
    path_from_module_to_file = strip_path_prefix(path, module_path or root)
    return module_path, path_to_pypath(path_from_module_to_file)


def import_user_predictor(entrypoint: Path, root=Path(".")) -> None:
    module_path, python_path = get_module_path_and_python_path(entrypoint, root)
    import_user_module(module_path, python_path)
