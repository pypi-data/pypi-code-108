import importlib
import inspect

from typing import Callable


def get_class(module_name: str, module_path: str) -> tuple[str, Callable]:
    """Retrieves the correct class name of a module"""

    # Import the module
    module = importlib.import_module(module_name, module_path)

    for class_name, class_def in inspect.getmembers(module, inspect.isclass):
        if class_name.lower() == module_name.lower().split(".")[-1]:
            return class_name, class_def

    raise ModuleNotFoundError(
        f"Couldnt find corresponding class {module_name} in {module_path}."
    )
