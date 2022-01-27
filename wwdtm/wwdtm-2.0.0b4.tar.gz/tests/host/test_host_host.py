# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object: :py:class:`wwdtm.host.Host`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.host import Host


@pytest.mark.skip
def get_connect_dict() -> Dict[str, Any]:
    """Read in database connection settings and return values as a
    dictionary.

    :return: A dictionary containing database connection settings
        for use by mysql.connector
    """
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
        if "database" in config_dict:
            return config_dict["database"]


def test_host_retrieve_all():
    """Testing for :py:meth:`wwdtm.host.Host.retrieve_all`
    """
    host = Host(connect_dict=get_connect_dict())
    hosts = host.retrieve_all()

    assert hosts, "No hosts could be retrieved"
    assert "id" in hosts[0], "'id' was not returned for the first list item"


def test_host_retrieve_all_details():
    """Testing for :py:meth:`wwdtm.host.Host.retrieve_all_details`
    """
    host = Host(connect_dict=get_connect_dict())
    hosts = host.retrieve_all_details()

    assert hosts, "No hosts could be retrieved"
    assert "id" in hosts[0], "'id' was not returned for first list item"
    assert "appearances" in hosts[0], ("'appearances' was not returned for the"
                                       "first list item")


def test_host_retrieve_all_ids():
    """Testing for :py:meth:`wwdtm.host.Host.retrieve_all_ids`
    """
    host = Host(connect_dict=get_connect_dict())
    ids = host.retrieve_all_ids()

    assert ids, "No host IDs could be retrieved"


def test_host_retrieve_all_slugs():
    """Testing for :py:meth:`wwdtm.host.Host.retrieve_all_slugs`
    """
    host = Host(connect_dict=get_connect_dict())
    slugs = host.retrieve_all_slugs()

    assert slugs, "No host slug strings could be retrieved"


@pytest.mark.parametrize("host_id", [2])
def test_host_retrieve_by_id(host_id: int):
    """Testing for :py:meth:`wwdtm.host.Host.retrieve_by_id`

    :param host_id: Host ID to test retrieving host information
    """
    host = Host(connect_dict=get_connect_dict())
    info = host.retrieve_by_id(host_id)

    assert info, f"Host ID {host_id} not found"
    assert "name" in info, f"'name' was not returned for ID {host_id}"


@pytest.mark.parametrize("host_id", [2])
def test_host_retrieve_details_by_id(host_id: int):
    """Testing for :py:meth:`wwdtm.host.Host.retrieve_details_by_id`

    :param host_id: Host ID to test retrieving host details
    """
    host = Host(connect_dict=get_connect_dict())
    info = host.retrieve_details_by_id(host_id)

    assert info, f"Host ID {host_id} not found"
    assert "name" in info, f"'name' was not returned for ID {host_id}"
    assert "appearances" in info, f"'appearances' was not returned for ID {host_id}"


@pytest.mark.parametrize("host_slug", ["luke-burbank"])
def test_host_retrieve_by_slug(host_slug: str):
    """Testing for :py:meth:`wwdtm.host.Host.retrieve_by_slug`

    :param host_slug: Host slug string to test retrieving host
        information
    """
    host = Host(connect_dict=get_connect_dict())
    info = host.retrieve_by_slug(host_slug)

    assert info, f"Host slug {host_slug} not found"
    assert "name" in info, f"'name' was not returned for slug {host_slug}"


@pytest.mark.parametrize("host_slug", ["luke-burbank"])
def test_host_retrieve_details_by_slug(host_slug: str):
    """Testing for :py:meth:`wwdtm.host.Host.retrieve_details_by_slug`

    :param host_slug: Host slug string to test retrieving host details
    """
    host = Host(connect_dict=get_connect_dict())
    info = host.retrieve_details_by_slug(host_slug)

    assert info, f"Host slug {host_slug} not found"
    assert "name" in info, f"'name' was not returned for slug {host_slug}"
    assert "appearances" in info, f"'appearances' was not returned for slug {host_slug}"
