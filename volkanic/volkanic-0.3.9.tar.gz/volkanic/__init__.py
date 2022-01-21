#!/usr/bin/env python3
# coding: utf-8

__version__ = '0.3.9'

if __name__ == '__main__':
    print(__version__)

from volkanic.cmdline import CommandRegistry
from volkanic.environ import GlobalInterface

# will be removed in 0.4.0
from volkanic.system import CommandConf
