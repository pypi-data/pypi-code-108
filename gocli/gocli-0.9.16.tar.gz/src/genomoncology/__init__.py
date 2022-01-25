import urllib3

from .state import State

from . import cli

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


__author__ = """Ian Maurer"""
__email__ = "ian@genomoncology.com"
__version__ = cli.commands.VERSION

__uri__ = "http://pypi.org/project/gocli"
__copyright__ = "Copyright (c) 2018 genomoncology.com"
__description__ = "gocli: GenomOncology Command Line Interface"
__doc__ = __description__ + " <" + __uri__ + ">"
__title__ = "gocli"


__all__ = ("State", "cli")
