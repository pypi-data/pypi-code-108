"""    
    External interface to use the interface programatically
    In this situation the environment should also be changed programatically
"""
from functools import partial
import lhapdf_management.configuration
from lhapdf_management.scripts.lhapdf_script import Runner


def _runner(mode, *args):
    runner = Runner(interactive=True)
    return getattr(runner, mode)(*args)


pdf_install = partial(_runner, "install")
pdf_update = partial(_runner, "update")
pdf_list = partial(_runner, "list")

environment = lhapdf_management.configuration.environment
