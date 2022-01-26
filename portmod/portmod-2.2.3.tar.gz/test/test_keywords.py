# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import pytest

from portmod.repo.keywords import accepts

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    yield dictionary
    tear_down_env()


def test_stable_visibility():
    assert accepts(["test"], ["test"])
    assert not accepts(["test"], ["test2"])
    assert accepts(["~test"], ["test"])
    assert accepts(["~*"], ["test"])
    assert accepts(["*"], ["test"])


def test_wild_stable_visibility():
    assert accepts(["test"], ["*", "test2"])
    assert accepts(["~test"], ["*", "test2"])
    assert accepts(["test"], ["*", "test"])
    assert accepts(["~test"], ["*", "test"])


def test_wild_testing_visibility():
    assert accepts(["~test"], ["~*", "test2"])
    assert accepts(["~test"], ["~*", "~test2"])
    assert not accepts(["test"], ["~*", "test2"])
    assert not accepts(["test"], ["~*", "~test2"])


def test_testing_visibility():
    assert not accepts(["test"], ["~test"])
    assert accepts(["~test"], ["~test"])
    assert accepts(["~*"], ["~test"])
    assert not accepts(["*"], ["~test"])


def test_wild_visibility():
    assert accepts(["test"], ["**"])
    assert accepts(["~test"], ["**"])
    assert accepts([], ["**"])


def test_untested_visibility():
    assert not accepts(["test"], [])
    assert not accepts(["~test"], [])
    assert accepts(["**"], [])
