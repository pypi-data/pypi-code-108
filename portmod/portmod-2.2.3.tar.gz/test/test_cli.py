# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests some otherwise untested parts of the interface
"""

import sys

import pytest

from portmod._cli.main import main


def test_version():
    """Tests that portmod --version works correctly"""
    sys.argv = ["portmod", "--version"]
    with pytest.raises(SystemExit):
        main()
