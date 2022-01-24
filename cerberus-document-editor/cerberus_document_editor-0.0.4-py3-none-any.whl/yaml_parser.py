import os
import io
import re
import yaml
from collections import OrderedDict
try:
    from yaml import CLoader as BaseLoader, CDumper as Dumper
except ImportError:
    from yaml import Loader as BaseLoader, Dumper
from functools import lru_cache

class Loader(BaseLoader):
    def __init__(self, stream):
        super(Loader, self).__init__(stream)

    interpolation_matcher = re.compile(r'\$\{([\w.-]+)(|:-([^}^{]+))\}')
    def interpolation(self, node):
        ''' Extract the matched value, expand env variable, and replace the match '''
        value = node.value
        match = self.interpolation_matcher.match(value)
        env_var = match.group(1)
        default = match.group(3) or value
        if not env_var.startswith('.'):
            return os.environ.get(env_var, default) + value[match.end():]
        else:
            return os.environ.get(env_var, default) + value[match.end():]

Loader.add_implicit_resolver('!interp', Loader.interpolation_matcher, None)
Loader.add_constructor('!interp', Loader.interpolation)

@lru_cache(maxsize=None)
def load(file):
    def sub_load(file):
        if isinstance(file, io.IOBase):
            stream = file.read()
        elif isinstance(file, str) and os.path.isfile(file):
            with open(file) as f:
                stream = f.read()
        else:
            stream = file   
        for _ in re.finditer(r'!include\s+([\w.-]+)', stream):
            stream = stream.replace(_.group(0), sub_load(os.path.join(os.getcwd(), _.group(1))))
        return stream
    def drop_recursive(data):
        _data = {}
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    v = drop_recursive(v)
                if not k.startswith('x-'):
                    _data[k] = v
        return _data
    return drop_recursive(yaml.load(sub_load(file), Loader=Loader))

def dump(doc):
    return yaml.dump(doc, Dumper=Dumper, default_flow_style=False, sort_keys=False)
