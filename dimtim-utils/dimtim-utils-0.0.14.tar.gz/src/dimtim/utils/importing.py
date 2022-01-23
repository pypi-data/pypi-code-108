import sys
from importlib import import_module


def safe_import(module: str, silence: bool = True, reraise: bool = False):
    try:
        return import_module(module)
    except ImportError as e:
        if not silence:
            sys.stdout.write(f'Module {module} importing error: {e}\n')
        if reraise:
            raise e
