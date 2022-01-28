import importlib.abc
import importlib.util
import os
import sys
from typing import Final, cast

ENTRYPOINT_FILENAMES: Final = [
    "jetpack_main.py",
    "main.py",
]


class EntrypointNotFoundException(Exception):
    pass


def load_user_entrypoint(user_entrypoint: str) -> None:
    entrypoint = _try_to_find_entrypoint(user_entrypoint)

    # We ensure the entrypoint path is in path so that imports work as expected.
    sys.path.append(os.path.dirname(entrypoint))
    module_name = _module_name(entrypoint)
    spec = importlib.util.spec_from_file_location(module_name, entrypoint)
    assert spec is not None
    entrypoint_module = importlib.util.module_from_spec(spec)
    cast(importlib.abc.Loader, spec.loader).exec_module(entrypoint_module)


def _try_to_find_entrypoint(user_entrypoint: str) -> str:
    """
    We try default or supplied entry point. if those don't work, we also try
    the current directory. This is a convenience for user using sdk cli
    directly
    """
    for entrypoint in [user_entrypoint, ""]:
        if os.path.isfile(entrypoint):
            return entrypoint
        for base in ENTRYPOINT_FILENAMES:
            full_path = os.path.join(entrypoint, base)
            if os.path.isfile(full_path):
                return full_path
    raise EntrypointNotFoundException(f"Entrypoint {user_entrypoint} not found")


def _module_name(entrypoint_with_filename: str) -> str:
    """
    Best guess as to the correct module name. Return $JETPACK_MODULE_NAME but
    default to relative path to entrypoint
    """
    if os.getenv("JETPACK_MODULE_NAME"):
        return cast(str, os.getenv("JETPACK_MODULE_NAME"))
    # remove the extension (e.g. foo/main.py -> foo/main)
    entrypoint, _ = os.path.splitext(entrypoint_with_filename)
    return os.path.relpath(entrypoint, os.getcwd()).replace("/", ".")
