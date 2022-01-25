from .construct import construct_sdk
from .variables import get_variable
from . import logger, models

__all__ = ("construct_sdk", "get_variable", "logger", "models")

__author__ = """Ian Maurer"""
__email__ = "ian@genomoncology.com"
__version__ = "0.8.18"

__uri__ = "http://pypi.org/project/gosdk"
__copyright__ = "Copyright (c) 2018 genomoncology.com"
__description__ = "govcf: GenomOncology Software Development Kit"
__doc__ = __description__ + " <" + __uri__ + ">"
__title__ = "gosdk"
