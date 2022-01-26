# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests modifying user use flags
"""

import pytest

from portmod.config import get_config
from portmod.config.use import add_use, get_use, remove_use
from portmod.loader import load_pkg
from portmod.merge import configure
from portmodlib.atom import Atom

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup_repo():
    """sets up and tears down test environment"""
    dictionary = setup_env("test")
    dictionary["modname"] = Atom("test/test-1.0-r2")
    configure([dictionary["modname"]], no_confirm=True)
    dictionary["mod"] = load_pkg(dictionary["modname"])[0]
    yield dictionary
    tear_down_env()


def test_add_remove_global():
    """tests adding and removing global use flags"""
    assert not get_config().get("USE", [])

    add_use("test1")
    assert "test1" in get_config().get("USE", [])

    remove_use("test1")
    assert not get_config().get("USE", [])


def test_disable_global():
    add_use("test1", disable=True)
    assert {"-test1"} == get_config().get("USE", [])
    remove_use("test1")
    assert not get_config().get("USE", [])


def test_disable_reenable_global():
    add_use("test1")
    add_use("test1", disable=True)
    assert {"-test1"} == get_config().get("USE", [])
    add_use("test2")
    assert {"-test1", "test2"} == get_config().get("USE", [])

    remove_use("test1")
    assert {"test2"} == get_config().get("USE", [])
    remove_use("test2")


def test_add_remove_mod(setup_repo):
    """tests adding and removing mod-specific use flags"""
    mod = setup_repo["mod"]
    modname = setup_repo["modname"]

    enabled, disabled = get_use(mod)
    assert not enabled
    assert not disabled

    add_use("test1", modname)
    assert "test1" in get_use(mod)[0]

    remove_use("test1", modname)
    assert not get_use(mod)[0]
    assert not get_use(mod)[1]


def test_add_remove_global_mod(setup_repo):
    """tests effects of global flags on mod flags"""
    mod = setup_repo["mod"]

    add_use("test1")
    assert "test1" in get_use(mod)[0]

    remove_use("test1")
    assert not get_use(mod)[0]
    assert not get_use(mod)[1]


def test_disable_modflags(setup_repo):
    """tests effects of disabled mod flags"""
    mod = setup_repo["mod"]
    modname = setup_repo["modname"]

    add_use("test1", modname, disable=True)
    assert {"test1"} == get_use(mod)[1]
    remove_use("test1", modname)
    assert not get_use(mod)[1]


def test_disable_global_on_modflags(setup_repo):
    """tests effects of disabled global flags on mod flags"""
    mod = setup_repo["mod"]

    add_use("test1", disable=True)
    assert {"test1"} == get_use(mod)[1]
    remove_use("test1")
    assert not get_use(mod)[1]


def test_disable_reenable_modflags(setup_repo):
    """tests effects of disabling then reenabling modflags"""
    mod = setup_repo["mod"]
    modname = setup_repo["modname"]

    add_use("test1", modname)
    add_use("test1", modname, disable=True)
    assert {"test1"} == get_use(mod)[1]
    add_use("test2", modname)
    assert {"test2"} == get_use(mod)[0]
    assert {"test1"} == get_use(mod)[1]

    remove_use("test1", modname)
    assert {"test2"} == get_use(mod)[0]
    assert not get_use(mod)[1]


def test_disable_reenable_global_modflags(setup_repo):
    """tests effects of disabling then reenabling global flags on modflags"""
    mod = setup_repo["mod"]

    add_use("test1")
    add_use("test1", disable=True)
    assert {"test1"} == get_use(mod)[1]
    add_use("test2")
    assert {"test2"} == get_use(mod)[0]
    assert {"test1"} == get_use(mod)[1]

    remove_use("test1")
    assert {"test2"} == get_use(mod)[0]
    assert not get_use(mod)[1]


def test_texture_size_override(setup_repo):
    """
    Tests that manually setting texture_size flags overrides
    the auto-selected version correctly
    """
    pkg = load_pkg(Atom("test/test-2.0"))[0]
    assert "texture_size_512" in pkg.get_use()
    add_use("texture_size_1024", Atom("test/test-2.0"))
    assert "texture_size_512" not in pkg.get_use()
    assert "texture_size_1024" in pkg.get_use()
