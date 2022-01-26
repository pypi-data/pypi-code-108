# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests the news subsystem
"""

import os
import sys

import pytest

from portmod._cli.main import main
from portmod.globals import env
from portmod.merge import configure
from portmod.news import (
    display_unread_message,
    iterate_news,
    mark,
    read_news,
    update_news,
)
from portmod.repo import get_repo
from portmodlib.parsers.list import read_list

from .env import select_profile, setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=False)
def setup():
    """sets up and tears down test environment"""
    dictionary = setup_env("test")
    yield dictionary
    tear_down_env()


def test_news(setup):
    update_news()

    news_dir = os.path.join(env.prefix().VARIABLE_DATA, "news")
    unread_file = os.path.join(news_dir, "news-test.unread")
    read_file = os.path.join(news_dir, "news-test.read")

    # Check that no news (all news is old news) is unread
    assert not os.path.exists(unread_file) or not read_list(unread_file)

    mark(get_repo("test"), "2020-04-12-test", read=False)
    # Check that article is now unread
    assert "2020-04-12-test" in read_list(unread_file)

    display_unread_message()

    read_news()
    # Check that article is now read
    assert "2020-04-12-test" not in read_list(unread_file)
    assert "2020-04-12-test" in read_list(read_file)


def test_news_installed(setup):
    update_news()

    assert "2020-04-12-installed" not in [
        os.path.basename(article)
        for article in iterate_news(get_repo("test"), visible_only=True)
    ]

    configure(["test/test-1.0"], no_confirm=True)
    assert "2020-04-12-installed" in [
        os.path.basename(article)
        for article in iterate_news(get_repo("test"), visible_only=True)
    ]

    configure(["test/test-2.0"], no_confirm=True)
    assert "2020-04-12-installed" not in [
        os.path.basename(article)
        for article in iterate_news(get_repo("test"), visible_only=True)
    ]

    configure(["test/test"], no_confirm=True, depclean=True)
    assert "2020-04-12-installed" not in [
        os.path.basename(article)
        for article in iterate_news(get_repo("test"), visible_only=True)
    ]


def test_news_profile(setup):
    update_news()

    assert "2020-04-12-profile" not in [
        os.path.basename(article)
        for article in iterate_news(get_repo("test"), visible_only=True)
    ]

    select_profile("test-config")
    assert "2020-04-12-profile" in [
        os.path.basename(article)
        for article in iterate_news(get_repo("test"), visible_only=True)
    ]


def test_news_cli(setup):
    sys.argv = ["portmod", "test", "select", "news", "list"]
    main()

    sys.argv = ["portmod", "test", "select", "news", "unread", "0"]
    main()

    sys.argv = ["portmod", "test", "select", "news", "read"]
    main()
