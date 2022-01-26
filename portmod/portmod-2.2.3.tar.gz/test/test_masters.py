# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests file master detection
"""

import os

import pytest

from portmod.globals import env
from portmod.merge import configure
from portmodlib.masters import get_masters

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup_repo():
    """sets up and tears down test environment"""
    yield setup_env("test")
    tear_down_env()


def test_masters_esp():
    """Tests that we detect esp masters properly"""

    configure(["test/quill-of-feyfolken-2.0.2"], no_confirm=True)
    path = os.path.join(
        env.prefix().ROOT, "pkg", "test", "quill-of-feyfolken", "Quill of Feyfolken.esp"
    )
    masters = get_masters(path)
    assert len(masters) == 1
    assert "Morrowind.esm" in masters
