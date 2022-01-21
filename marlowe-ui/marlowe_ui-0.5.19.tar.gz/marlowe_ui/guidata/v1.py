import copy

from .. import layoutmode

from . import solve_version_factory
from . import v0 as prev
from .v0 import *  # noQA

version = 1

app_default = {'root': prev.root_default,
               'gui_layout': layoutmode.mode_default,
               'version': version}

app_example = {'root': prev.root_example,
               'gui_layout': layoutmode.mode_example,
               'version': version}

default = app_default
example = app_example


def _update_prevonly(d):
    newd = copy.deepcopy(default)
    newd['root'] = copy.deepcopy(d)
    return newd

# def solve_update(d)
solve_version = solve_version_factory.solve_version_factory(
    version, _update_prevonly, prev.solve_version)
