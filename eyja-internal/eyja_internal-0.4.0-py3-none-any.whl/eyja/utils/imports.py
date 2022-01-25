import importlib
import inspect

from eyja.hubs.config_hub import ConfigHub


def load_class(class_path):
    parts = class_path.split('.')
    module_path = '.'.join(parts[:-1])
    module = importlib.import_module(module_path)
    cls = getattr(module, parts[-1])
    if inspect.isclass(cls):
        return cls
    
    return None

def load_model(class_path, default_cls):
    model_path = ConfigHub.get(class_path)
    if not model_path:
        return default_cls    
    return load_class(model_path)
