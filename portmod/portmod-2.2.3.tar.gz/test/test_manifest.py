# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os

import pytest

from portmod._cli.pybuild import pybuild_manifest
from portmod.globals import env
from portmod.repo import get_repo

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    yield dictionary
    tear_down_env()


def test_manifest():
    """Tests that a manifests can be generated without a prefix set"""
    env.set_prefix(None)
    env.ALLOW_LOAD_ERROR = False
    path = os.path.join(
        get_repo("test").location,
        "test",
        "quill-of-feyfolken",
        "quill-of-feyfolken-2.0.2.pybuild",
    )
    pybuild_manifest(path)
