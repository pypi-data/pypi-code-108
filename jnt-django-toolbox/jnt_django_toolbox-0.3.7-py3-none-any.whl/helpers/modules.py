import importlib
from contextlib import suppress


def load_module_from_app(app_config, dotted_path: str):
    """Load module from application."""
    module_name = "{0}.{1}".format(app_config.name, dotted_path)
    module_spec = None

    with suppress(ModuleNotFoundError):
        module_spec = importlib.util.find_spec(module_name)  # type: ignore

    if module_spec:
        return importlib.import_module(module_name)
