# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import sys

import pytest

from portmod._cli.main import main
from portmod.globals import env
from portmod.merge import configure
from portmod.modules import get_redirections

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    os.makedirs(env.prefix().CONFIG_PROTECT_DIR, exist_ok=True)
    yield dictionary
    tear_down_env()


def test_module(setup):
    """Tests that modules work as expected"""
    configure(["test/test-module"], no_confirm=True)
    assert os.path.exists(
        os.path.join(env.prefix().CONFIG_PROTECT_DIR, "foo.cfg_protect")
    )
    assert get_redirections()


def test_module_cli(setup):
    """Tests that the CLI module interface works"""
    configure(["test/test-module"], no_confirm=True)
    sys.argv = ["portmod", "test", "select", "test-module", "list"]
    main()
