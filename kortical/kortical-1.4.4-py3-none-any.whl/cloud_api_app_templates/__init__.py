import os
import inspect

_templates_directory = None


def get_templates_directory():
    global _templates_directory
    if _templates_directory is not None:
        return _templates_directory

    _templates_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return _templates_directory
