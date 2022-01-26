# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests the mod selection system
"""

import pytest

from portmod.loader import load_pkg
from portmodlib.atom import Atom

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    yield setup_env("test")
    tear_down_env()


def test_moved():
    """Tests that moved atoms are loaded when the old name is used"""
    pkgs = load_pkg(Atom("test2/test-old"))
    assert any(pkg.CPN == "test/test-new" for pkg in pkgs)
