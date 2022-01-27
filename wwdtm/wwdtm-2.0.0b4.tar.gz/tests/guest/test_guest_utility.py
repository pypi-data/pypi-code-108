# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object: :py:class:`wdtm.guest.GuestUtility`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.guest import GuestUtility


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


@pytest.mark.parametrize("guest_id", [54])
def test_guest_utility_convert_id_to_slug(guest_id: int):
    """Testing for :py:meth:`wwdtm.guest.GuestUtility.convert_id_to_slug`

    :param guest_id: Guest ID to test converting into guest slug string
    """
    utility = GuestUtility(connect_dict=get_connect_dict())
    slug = utility.convert_id_to_slug(guest_id)

    assert slug, f"Guest slug for ID {guest_id} was not found"
    assert isinstance(slug, str), f"Invalid value returned for ID {guest_id}"


@pytest.mark.parametrize("guest_id", [-54])
def test_guest_utility_convert_invalid_id_to_slug(guest_id: int):
    """Negative testing for :py:meth:`wwdtm.guest.GuestUtility.convert_id_to_slug`

    :param guest_id: Guest ID to test failing to convert into guest slug
        string
    """
    utility = GuestUtility(connect_dict=get_connect_dict())
    slug = utility.convert_id_to_slug(guest_id)

    assert not slug, f"Guest slug for ID {guest_id} was found"


@pytest.mark.parametrize("guest_slug", ["tom-hanks", "stephen-colbert"])
def test_guest_utility_convert_slug_to_id(guest_slug: str):
    """Testing for :py:meth:`wwdtm.guest.GuestUtility.convert_slug_to_id`

    :param guest_slug: Guest slug string to test converting into guest
        ID
    """
    utility = GuestUtility(connect_dict=get_connect_dict())
    id_ = utility.convert_slug_to_id(guest_slug)

    assert id_, f"Guest ID for slug {guest_slug} was not found"
    assert isinstance(id_, int), f"Invalid value returned for slug {guest_slug}"


@pytest.mark.parametrize("guest_slug", ["tom-hanx", "steven-colbert"])
def test_guest_utility_convert_invalid_slug_to_id(guest_slug: str):
    """Negative testing for :py:meth:`wwdtm.guest.GuestUtility.convert_slug_to_id`

    :param guest_slug: Guest slug string to test failing to convert into
        guest ID
    """
    utility = GuestUtility(connect_dict=get_connect_dict())
    id_ = utility.convert_slug_to_id(guest_slug)

    assert not id_, f"Guest ID for slug {guest_slug} was found"


@pytest.mark.parametrize("guest_id", [54])
def test_guest_utility_id_exists(guest_id: int):
    """Testing for :py:meth:`wwdtm.guest.GuestUtility.id_exists`

    :param guest_id: Guest ID to test if a guest exists
    """
    utility = GuestUtility(connect_dict=get_connect_dict())
    result = utility.id_exists(guest_id)

    assert result, f"Guest ID {guest_id} does not exist"


@pytest.mark.parametrize("guest_id", [-1])
def test_guest_utility_id_not_exists(guest_id: int):
    """Negative testing for :py:meth:`wwdtm.guest.GuestUtility.id_exists`

    :param guest_id: Guest ID to test if a guest does not exist
    """
    utility = GuestUtility(connect_dict=get_connect_dict())
    result = utility.id_exists(guest_id)

    assert not result, f"Guest ID {guest_id} exists"


@pytest.mark.parametrize("guest_slug", ["tom-hanks", "stephen-colbert"])
def test_guest_utility_slug_exists(guest_slug: str):
    """Testing for :py:meth:`wwdtm.guest.GuestUtility.slug_exists`

    :param guest_slug: Guest slug string to test if a guest exists
    """
    utility = GuestUtility(connect_dict=get_connect_dict())
    result = utility.slug_exists(guest_slug)

    assert result, f"Guest slug {guest_slug} does not exist"


@pytest.mark.parametrize("guest_slug", ["tom-hanx", "steven-colbert"])
def test_guest_utility_slug_not_exists(guest_slug: str):
    """Negative testing for :py:meth:`wwdtm.guest.GuestUtility.slug_exists`

    :param guest_slug: Guest slug string to test if a guest does not
        exist
    """
    utility = GuestUtility(connect_dict=get_connect_dict())
    result = utility.slug_exists(guest_slug)

    assert not result, f"Guest slug {guest_slug} exists"
