#!/usr/bin/env python3

import os,sys
from pathlib import Path
from make_var import *
import pytest


def test_make_vars():
    # set directory to Makefile place
    fdir = Path(__file__).parent
    os.chdir(fdir)

    M=make_vars(origin=['makefile']) # retrieve only data defined in makefiles
    s = f"{M['makefile']['H']}, {M['makefile']['W']}"
    print(M['makefile']['H'], M['makefile']['W'])

    assert(s == "hello, world")


if __name__ == "__main__":
    test_make_vars()
