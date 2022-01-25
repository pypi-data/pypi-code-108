import os
import importlib.abc
import importlib.util
import sys
import sbol3


class Loader(importlib.abc.Loader):

    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table = symbol_table

    def create_module(self, spec):
        return None
    
    def exec_module(self, module):
        for symbol, obj in self.symbol_table.items():
            module.__dict__[symbol] = obj

class SBOLFactory():

    def __new__(cls, module_name):
        spec = importlib.util.spec_from_loader(
            module_name,
            Loader({})
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        cls.__init__(module, 'bar', None, None)
        print('new')
        return module

    def __init__(self, foo1, foo2, foo3):
        print('init')
        self.foo = foo1

def create_module(module_name):
    spec = importlib.util.spec_from_loader(
        module_name,
        Loader(sbol3.__dict__)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module

foo = SBOLFactory('bar')
