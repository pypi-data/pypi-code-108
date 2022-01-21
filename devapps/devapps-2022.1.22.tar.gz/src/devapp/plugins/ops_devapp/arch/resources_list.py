#!/usr/bin/env python
"""
Listing All Defined Resources

We scan ALL modules for an operations.resources.py
"""


import os, sys
from functools import partial
import importlib
from devapp.app import app, do, run_app, system
from devapp.tools import FLG, project, exists, repl_dollar_var_with_env_val

from . import _resources_api as api


class Flags(api.CommonFlags):
    pass


# ------------------------------------------------------------------------- end actions
def run():
    rscs = do(api.find_resource_defs)
    if FLG.install_state:
        do(api.add_install_state, rscs=rscs)
    l = api.to_list(rscs)
    return l


main = partial(run_app, run, flags=Flags)
