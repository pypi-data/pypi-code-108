from enum import Enum
from decimal import Decimal
from typing import Callable
import consul
from jcramda import identity, decode
try:
    import hcl
    HasHcl = True
    def _hcl_load(raw_value):
        return hcl.loads(raw_value)
except ModuleNotFoundError:
    HasHcl = False


__all__ = (
    'Consul',
    'path_join',
    'fetch_key',
    'register_service',
    'deregister',
)

Consul = consul.Consul


def path_join(*args):
    return '/'.join(args)


def _yaml_load(raw_value):
    import yaml
    return yaml.safe_load(raw_value)


def _json_load(raw_value):
    import json
    return json.loads(raw_value)

class ConfigFormat(Enum):
    Text = decode 
    Number = Decimal
    Int = int
    Float = float
    Json = _json_load
    Yaml = _yaml_load
    Hcl = _hcl_load if HasHcl else lambda _: None


def fetch_key(key_path, fmt: Callable = None):
    __, raw = Consul().kv.get(key_path)
    assert raw, f'not found any content in {key_path}'
    # noinspection PyCallingNonCallable
    values = raw.get('Value')
    return fmt(values) if callable(fmt) else values.decode()
    

def register_service(service_name, **kwargs):
    """

    Parameters
    ----------
    service_name
    kwargs

    See Also
    -----------
    consul.base.Service
    """
    c = Consul()
    c.agent.service.register(service_name, **kwargs)


def deregister(service_id):
    Consul().agent.service.deregister(service_id)


class KvProperty:
    def __init__(self, key, /, prefix=None, namespace=None, format=None, cached=None):
        self.key = key
        self._prefix = '/'.join(filter(None, (namespace or 'properties', prefix)))
        self._fmt = format or ConfigFormat.Text
        self._cached = cached
    
    def __get__(self, instance, cls):
        if instance is None:
            print(cls)
            return cls
        if callable(self.key):
            name = self.key.__name__
            func = self.key
        else:
            name = self.key
            func = identity
        value = func(fetch_key('/'.join([self._prefix, instance.__class__.__name__, name]), self._fmt))
        if self._cached:
            setattr(instance, name, value)
        return value
