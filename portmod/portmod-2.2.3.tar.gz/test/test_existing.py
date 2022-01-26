# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests support for installing on top of existing data
"""

import os
import sys

import pytest

from portmod._cli.main import main
from portmod._cli.select import add_prefix_repo
from portmod.config import get_config
from portmod.globals import env
from portmod.merge import configure
from portmodlib.atom import Atom

from .env import select_profile, setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    yield setup_env("base")
    tear_down_env()


def run(args):
    sys.argv = args
    main()


def test_init_destroy():
    """
    Tests that prefixes created on top of existing directories
    will not remove existing files on destruction
    """
    with open("existing_file", "w") as file:
        file.write("")

    run(["portmod", "init", "test2", "test", "."])
    run(["portmod", "test2", "destroy"])
    assert os.path.exists("existing_file")


def test_init_overlap():
    """Tests that you cannot create two prefixess with overlapping directories"""
    run(["portmod", "init", "test2", "test", "."])
    os.makedirs("foo", exist_ok=True)
    with pytest.raises(SystemExit):
        run(["portmod", "init", "test3", "test", "foo"])

    run(["portmod", "test2", "destroy"])

    run(["portmod", "init", "test2", "test", "foo"])
    with pytest.raises(SystemExit):
        run(["portmod", "init", "test3", "test", "."])

    run(["portmod", "test2", "destroy"])


@pytest.mark.skipif(
    sys.platform == "win32" and "APPVEYOR" in os.environ,
    reason="Windows CI is flaky with deleting git repositories",
)
def test_backup():
    """
    Tests that when packages overwrite existing data,
    it's restored after the package is removed
    """
    filepath = os.path.join("pkg", "test", "test", "Foo")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        file.write("bar")

    run(["portmod", "init", "test2", "test", "."])
    env.set_prefix("test2")
    add_prefix_repo("test")
    env.set_prefix("test2")
    select_profile("test")
    get_config.cache_clear()  # type: ignore

    configure([Atom("=test/test-1.0-r2")], no_confirm=True)
    with open(filepath) as file:
        assert file.read() != "bar"
    configure([Atom("test/test")], no_confirm=True, depclean=True)
    with open(filepath) as file:
        assert file.read() == "bar"

    run(["portmod", "test2", "destroy"])
