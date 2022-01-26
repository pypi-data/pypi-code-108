# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests modifying user use flags
"""

import os
import sys
from io import StringIO

import pytest

import portmodlib.log as log
from portmod._cli.main import main
from portmod.globals import env
from portmod.repos import get_repos
from portmod.sync import sync

from .env import setup_env, tear_down_env, unset_profile


@pytest.fixture(scope="module", autouse=True)
def setup():
    """sets up and tears down test environment"""
    dictionary = setup_env("test")
    env.REPOS = get_repos()
    # Unset profile so news is marked as old
    unset_profile()
    yield dictionary
    tear_down_env()


@pytest.mark.skipif(
    sys.platform == "win32" and "APPVEYOR" in os.environ,
    reason="Windows CI is flaky with deleting git repositories",
)
def test_logging():
    """Tests that verbose and quiet control output verbosity"""
    oldargs = sys.argv
    sync(env.REPOS)
    sys.argv = ["portmod", "sync", "--quiet"]
    output = StringIO()

    # Note: Logging cannot be redirected with redirect_stderr,
    # as the output stream is set on logger initialization
    log._LOG_HANDLER.__init__(output)  # type: ignore

    main()

    assert not output.getvalue()

    sys.argv = ["portmod", "sync", "--verbose"]
    output = StringIO()
    log._LOG_HANDLER.__init__(output)  # type: ignore
    main()

    assert output.getvalue()

    sys.argv = oldargs
    log._LOG_HANDLER.__init__(sys.stderr)  # type: ignore
