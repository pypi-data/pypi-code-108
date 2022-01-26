# -*- coding: utf8 -*-  

""" package in order to reduce and analyze fits 

:author: Clement Hottier
"""


from .utils import makemasterbias, makemasterflat, processimages, crosscorrelalign, alignstack, clean_cosmic


__author__ = "Clement Hottier, Noel Robichon"
__version__ = "1.1.3"
__all__ = [
        "makemasterbias",
        "makemasterflat",
        "processimages",
        "crosscorrelalign",
        "alignstack",
        "clean_cosmic",
]
