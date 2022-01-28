import sys
from importlib import import_module
from types import ModuleType

from . import __name__ as _module_name


def _get_command() -> str:
    command: str = ""
    if len(sys.argv) > 1:
        command = sys.argv.pop(1).lower().replace("-", "_")
    return command


def main() -> None:
    """
    Run a sub-module `main` function.
    """
    command = _get_command()
    module: ModuleType
    try:
        module = import_module(f"{_module_name}.{command}.__main__")
    except ImportError:
        module = import_module(f"{_module_name}.{command}")
    module.main()  # type: ignore


if __name__ == "__main__":
    main()
