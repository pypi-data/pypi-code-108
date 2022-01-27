from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module


def load_plugins():
    """Load all plugins in the plugins directory"""
    path = get_path_to_plugins()
    path = Path(path)
    modules = []
    for _, name, _ in iter_modules([str(path)]):
        if not name.startswith('__'):
            module = import_module(f'.{name}', package=__name__)
            modules.append(module)
    return modules

def get_path_to_plugins():
    """Get the path to the plugins directory"""
    return Path(__file__).parent.parent / 'plugins'
