# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests some otherwise untested parts of the interface
"""

import io
import os
import sys

import pytest

from portmod._cli.main import main
from portmod.globals import env
from portmod.loader import load_installed_pkg
from portmodlib.atom import Atom

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    yield setup_env("test")
    tear_down_env()


def test_validate():
    """Tests that validate works correctly"""
    sys.argv = ["portmod", "test", "merge", "test", "test2", "--no-confirm"]
    main()
    sys.argv = ["portmod", "test", "validate"]
    main()


@pytest.mark.skipif(
    sys.platform == "win32" and "APPVEYOR" in os.environ,
    reason="Windows CI is flaky with deleting git repositories",
)
def test_sync():
    """Tests that portmod sync works correctly"""
    sys.argv = ["portmod", "sync"]
    main()


def test_info():
    """Tests that portmod info works correctly"""
    sys.argv = ["portmod", "test", "info"]
    with pytest.raises(SystemExit):
        main()


def test_search(monkeypatch):
    """Tests that portmod search works correctly"""
    sys.argv = ["portmod", "test", "search", "test"]
    monkeypatch.setattr("sys.stdin", io.StringIO("\n"))
    main()


def test_use():
    """Tests that portmod use works correctly"""
    sys.argv = ["portmod", "test", "use", "-E", "foo"]
    main()
    sys.argv = ["portmod", "test", "merge", "test4", "--no-confirm"]
    main()
    pkg = load_installed_pkg(Atom("test/test4"))
    assert pkg
    assert "foo" in pkg.get_use()


def test_mirror():
    """Tests that portmod --version works correctly"""
    sys.argv = ["portmod", "mirror", os.path.join(env.TMP_DIR, "mirror")]
    main()
