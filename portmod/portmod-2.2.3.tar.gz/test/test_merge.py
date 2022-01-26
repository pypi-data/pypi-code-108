# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import pytest

from portmod.loader import load_installed_pkg
from portmod.merge import configure
from portmodlib.atom import Atom

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    yield dictionary
    tear_down_env()


def test_nodeps_use_dependency(setup):
    """Tests that simple dependency resolution works"""
    configure(["=test/test7-1.0[baz]"], no_confirm=True, nodeps=True)
    # A dependency which would otherwise be pulled in by baz, but nodeps should ignore it
    assert not load_installed_pkg(Atom("test/test5"))
    pkg = load_installed_pkg(Atom("test/test7"))
    assert pkg
    assert "baz" in pkg.INSTALLED_USE
