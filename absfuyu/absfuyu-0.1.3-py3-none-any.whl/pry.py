#!/usr/bin/env python
# coding: utf-8
"""
Pry Module
----------
"""


# Module level
##############################################################
__all__ = [
    "srcMe",
]




# Library
##############################################################
from inspect import getsource as src
from typing import Any






# Function
##############################################################

def srcMe(function: Any) -> str:
    """
    Summary
    -------
    Show the source code of a function

    Parameters
    ----------
    function : Any
        just input the function name

    Returns
    -------
    Source code
    """

    return src(function)




if __name__ == "__main__":
    pass