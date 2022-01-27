# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import pkgutil
import importlib

from .backends import layers
from .backends import systems


LAYER_MOD_PATH = 'backends.layers'
BACKEND_MOD_PATH = 'backends.systems'


class LazyModuleDict(dict):
    """Import modules lazy on access."""

    def __init__(self, module):
        super(LazyModuleDict, self).__init__()
        self.path = module.__path__
        for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
            self[modname] = importer.find_module(modname)

    @staticmethod
    def __import_children(item, full_modname, path):
        for importer, modname, ispkg in pkgutil.iter_modules(
                path):
            # TODO(stefan): Import backend modules lazily to avoid multiple
            #               backend imports.
            # Note: Importing using this method requires unique namespaces
            #       for each module, otherwise already existing modules
            #       are overwritten since a module reload is performed on
            #       the existing module already in the self dictionary on
            #       another item. This is why full_modname is important.
            full_modname = '{}.{}'.format(full_modname, modname)
            module = (
                importer.find_module(full_modname).load_module(full_modname))
            item.__dict__[modname] = module

    def __getitem__(self, modname):
        item = super(LazyModuleDict, self).__getitem__(modname)
        if isinstance(item, pkgutil.ImpLoader):
            full_modname = '{}.{}'.format(LAYER_MOD_PATH, modname)
            item = item.load_module(full_modname)
            self.__import_children(item, full_modname, item.__path__)
            super(LazyModuleDict, self).__setitem__(modname, item)
        elif isinstance(
                item, importlib.machinery.SourceFileLoader):
            lm = item.load_module(modname)
            full_modname = '{}.{}'.format(LAYER_MOD_PATH, modname)
            self.__import_children(item, full_modname, lm.__path__)
        return item


def get_layer_module(layer_name):
    return layer_modules[layer_name]


def get_layer_meta(layer_name):
    return get_layer_module(layer_name).layer.Layer.meta


def get_backend(backend_name):
    return backend_modules[backend_name].backend


layer_modules = LazyModuleDict(layers)
backend_modules = LazyModuleDict(systems)

available_plugins = {
    'layers': sorted(layer_modules.keys()),
    'systems': sorted(backend_modules.keys())
}
