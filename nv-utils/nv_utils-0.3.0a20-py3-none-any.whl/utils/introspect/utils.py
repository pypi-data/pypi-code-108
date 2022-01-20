from inspect import getmodule, ismethod
from typing import Callable, Type, Union
from types import ModuleType

"""
Based on https://stackoverflow.com/questions/3589311/get-defining-class-of-unbound-method-object-in-python-3

"""


def get_definition_scope(clb: Callable) -> Union[Type, ModuleType]:
    if ismethod(clb):
        clb = clb.__func__

    module = getmodule(clb)
    cls_name = clb.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
    cls = getattr(module, cls_name, None)
    return module if cls is clb else cls
