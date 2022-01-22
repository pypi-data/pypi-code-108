from collections import defaultdict
from functools import lru_cache
from importlib import import_module
from pkgutil import iter_modules

from pybrary.func import fqn
from pybrary.files import find
from pybrary.modules import load

from setux.logger import debug, info, error

import setux.core


@lru_cache()
def get_modules(ns):
    debug(f'{ns.__name__}')
    path, name = ns.__path__, ns.__name__ + '.'
    try:
        fil = None
        if hasattr(path, '_path'):                   # namespace
            found = list()
            for pth in path._path:
                debug(f'    {pth}')
                for fil in find(pth, r'\.py$'):
                    if fil.name=='__init__.py':
                        error(f' ! __init__ in ns {pth}')
                        return
                    nam = name+fil.stem
                    mod = load(nam, fil)
                    found.append((nam, mod))
            return found
        else:                                        # package
            return [
                (name, import_module(name))
                for finder, name, _ispkg in iter_modules(path, name)
            ]
    except Exception as x:
        error(f'\n ! {fil or name}\n ! {x}\n')


def get_raw_plugins(ns, cls):
    for mod, module in get_modules(ns):
        for plg, plugin in module.__dict__.items():
            try:
                if issubclass(plugin, cls):
                    yield mod, plg, plugin
            except TypeError: pass


def get_plugins(ns, cls):
    get_core = get_raw_plugins(setux.core, cls)
    core = set(cls for _m, _p, cls in get_core)
    return [
        (mod, plg, plugin)
        for mod, plg, plugin in get_raw_plugins(ns, cls)
        if plugin not in core
    ]


class Plugins:
    def __init__(self, distro, Base, ns):
        self.distro = distro
        self.Base = Base
        self.ns = ns
        self.items = dict()
        self.mappings = defaultdict(int)
        self.collect()

    def __iter__(self):
        return iter(self.items.values())

    def parse(self, mod, plg, plugin):
        return plg, plugin

    def sort(self):
        ''' sort self.items in place
        '''

    def collect(self):
        plugins = get_plugins(self.ns, self.Base)
        for mod, plg, plugin in plugins:
            key, val = self.parse(mod, plg, plugin)
            if key and val:
                self.items[key] = val
        self.sort()
        for mod in self:
            debug('%s registred', fqn(mod))


class Distros(Plugins):
    def sort(self):
        def sort_key(item):
            name, cls = item
            return len(cls.distro_lineage(cls))

        self.items = dict(
            item
            for item in reversed(sorted(
                self.items.items(),
                key = sort_key
            ))
        )


class DistroPlugins(Plugins):
    def parse(self, mod, plg, plugin):
        lineage = self.distro.lineage
        if plg in lineage:
            name = '.'.join(mod.split('.')[2:])
            old = self.items.get(name)
            if old:
                idx = lineage.index(plg)
                old_idx = lineage.index(old.__name__)
                if idx > old_idx:
                    return name, plugin
            else:
                return name, plugin
        return None, None


class Modules(DistroPlugins): pass


class Managers(DistroPlugins): pass


class Mappings(Plugins):
    def parse(self, mod, plg, plugin):
        if plg in self.distro.lineage:
            name = fqn(plugin)
            self.mappings[name]+=1
            name += f'_{self.mappings[name]}'
            return name, plugin
        return None, None

