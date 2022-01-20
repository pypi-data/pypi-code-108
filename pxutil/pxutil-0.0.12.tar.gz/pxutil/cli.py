#!/usr/bin/env python3
"""
pxutil CLI scripts

Refer: https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html
"""

import os
import sys
import logging
from pxutil import bashx

if sys.version_info < (3, 5):
    raise Exception("Require python 3.5 or above.")

def bashx_main():
    cmd = ' '.join(sys.argv[1:])
    bashx(cmd)
    
if __name__ == "__main__":
    bashx_main()