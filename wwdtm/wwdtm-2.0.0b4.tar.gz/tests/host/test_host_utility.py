# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object: :py:class:`wwdtm.host.HostUtility`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.host import HostUtility


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


@pytest.mark.parametrize("host_id", [2])
def test_host_utility_convert_id_to_slug(host_id: int):
    """Testing for :py:meth:`wwdtm.host.HostUtility.convert_id_to_slug`

    :param host_id: Host ID to test converting into host slug string
    """
    utility = HostUtility(connect_dict=get_connect_dict())
    slug = utility.convert_id_to_slug(host_id)

    assert slug, f"Host slug for ID {host_id} was not found"
    assert isinstance(slug, str), f"Invalid value returned for ID {host_id}"


@pytest.mark.parametrize("host_id", [-1])
def test_host_utility_convert_invalid_id_to_slug(host_id: int):
    """Negative testing for :py:meth:`wwdtm.host.HostUtility.convert_id_to_slug`

    :param host_id: Host ID to test failing to convert into host slug
        string
    """
    utility = HostUtility(connect_dict=get_connect_dict())
    slug = utility.convert_id_to_slug(host_id)

    assert not slug, f"Host slug for ID {host_id} was found"


@pytest.mark.parametrize("host_slug", ["tom-hanks"])
def test_host_utility_convert_slug_to_id(host_slug: str):
    """Testing for :py:meth:`wwdtm.host.HostUtility.convert_slug_to_id`

    :param host_slug: Host slug string to test converting into host ID
    """
    utility = HostUtility(connect_dict=get_connect_dict())
    id_ = utility.convert_slug_to_id(host_slug)

    assert id_, f"Host ID for slug {host_slug} was not found"
    assert isinstance(id_, int), f"Invalid value returned for slug {host_slug}"


@pytest.mark.parametrize("host_slug", ["tom-hanx"])
def test_host_utility_convert_invalid_slug_to_id(host_slug: str):
    """Negative testing for :py:meth:`wwdtm.host.HostUtility.convert_slug_to_id`

    :param host_slug: Host slug string to test failing to convert into
        host ID
    """
    utility = HostUtility(connect_dict=get_connect_dict())
    result = utility.convert_slug_to_id(host_slug)

    assert not result, f"Host ID for slug {host_slug} found"


@pytest.mark.parametrize("host_id", [2])
def test_host_utility_id_exists(host_id: int):
    """Testing for :py:meth:`wwdtm.host.HostUtility.id_exists`

    :param host_id: Host ID to test if a host exists
    """
    utility = HostUtility(connect_dict=get_connect_dict())
    result = utility.id_exists(host_id)

    assert result, f"Host ID {host_id} does not exist"


@pytest.mark.parametrize("host_id", [-1])
def test_host_utility_id_not_exists(host_id: int):
    """Negative testing for :py:meth:`wwdtm.host.HostUtility.id_exists()`

    :param host_id: Host ID to test if a host does not exist
    """
    utility = HostUtility(connect_dict=get_connect_dict())
    result = utility.id_exists(host_id)

    assert not result, f"Host ID {host_id} exists"


@pytest.mark.parametrize("host_slug", ["tom-hanks"])
def test_host_utility_slug_exists(host_slug: str):
    """Testing for :py:meth:`wwdtm.host.HostUtility.slug_exists`

    :param host_slug: Host slug string to test if a host exists
    """
    utility = HostUtility(connect_dict=get_connect_dict())
    result = utility.slug_exists(host_slug)

    assert result, f"Host slug {host_slug} does not exist"


@pytest.mark.parametrize("host_slug", ["tom-hanx"])
def test_host_utility_slug_not_exists(host_slug: str):
    """Negative testing for :py:meth:`wwdtm.host.HostUtility.slug_exists`

    :param host_slug: Host slug string to test if a host does not exist
    """
    utility = HostUtility(connect_dict=get_connect_dict())
    result = utility.slug_exists(host_slug)

    assert not result, f"Host slug {host_slug} exists"
