import inspect
import os
from pathlib import Path

root_path = None


def module_path(local_function):
    """
    returns the module path without the use of __file__.  Requires a function defined
    locally in the module.
    from https://stackoverflow.com/questions/729583/getting-file-path-of-imported-module
    """
    return os.path.abspath(inspect.getsourcefile(local_function))


def get_root_dir():
    global root_path
    if root_path is not None:
        return root_path
    path_to_module = Path(module_path(lambda: 0))
    root_path = str(path_to_module.parent.parent.parent)
    return root_path


def from_root_dir(path):
    return os.path.join(get_root_dir(), path)