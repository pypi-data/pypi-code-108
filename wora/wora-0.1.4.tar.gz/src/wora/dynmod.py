import importlib.util

def to_dict(**kwargs) -> dict:
    ''' Returns a dictionary from kwargs '''
    return kwargs

def module_from_file(module_name: str, file_path: str) -> module:
    ''' Returns a hookable python module from a given file path '''
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
