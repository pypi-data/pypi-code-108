# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object: :py:class:`wwdtm.guest.Guest`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.guest import Guest


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


def test_guest_retrieve_all():
    """Testing for :py:meth:`wwdtm.guest.Guest.retrieve_all`
    """
    guest = Guest(connect_dict=get_connect_dict())
    guests = guest.retrieve_all()

    assert guests, "No guests could be retrieved"
    assert "id" in guests[0], "'id' was not returned for the first list item"


def test_guest_retrieve_all_details():
    """Testing for :py:meth:`wwdtm.guest.Guest.retrieve_all_details`
    """
    guest = Guest(connect_dict=get_connect_dict())
    guests = guest.retrieve_all_details()

    assert guests, "No guests could be retrieved"
    assert "id" in guests[0], "'id' was not returned for first list item"
    assert "appearances" in guests[0], ("'appearances' was not returned for "
                                        "the first list item")


def test_guest_retrieve_all_ids():
    """Testing for :py:meth:`wwdtm.guest.Guest.retrieve_all_ids`
    """
    guest = Guest(connect_dict=get_connect_dict())
    ids = guest.retrieve_all_ids()

    assert ids, "No guest IDs could be retrieved"


def test_guest_retrieve_all_slugs():
    """Testing for :py:meth:`wwdtm.guest.Guest.retrieve_all_slugs`
    """
    guest = Guest(connect_dict=get_connect_dict())
    slugs = guest.retrieve_all_slugs()

    assert slugs, "No guest slug strings could be retrieved"


@pytest.mark.parametrize("guest_id", [976])
def test_guest_retrieve_by_id(guest_id: int):
    """Testing for :py:meth:`wwdtm.guest.Guest.retrieve_by_id`

    :param guest_id: Guest ID to test retrieving guest information
    """
    guest = Guest(connect_dict=get_connect_dict())
    info = guest.retrieve_by_id(guest_id)

    assert info, f"Guest ID {guest_id} not found"
    assert "name" in info, f"'name' was not returned for ID {guest_id}"


@pytest.mark.parametrize("guest_slug", ["tom-hanks"])
def test_guest_retrieve_by_slug(guest_slug: str):
    """Testing for :py:meth:`wwdtm.guest.Guest.retrieve_by_slug`

    :param guest_slug: Guest slug string to test retrieving guest
        information
    """
    guest = Guest(connect_dict=get_connect_dict())
    info = guest.retrieve_by_slug(guest_slug)

    assert info, f"Guest slug {guest_slug} not found"
    assert "name" in info, f"'name' was not returned for slug {guest_slug}"


@pytest.mark.parametrize("guest_id", [976])
def test_guest_retrieve_details_by_id(guest_id: int):
    """Testing for :py:meth:`wwdtm.guest.Guest.retrieve_details_by_id`

    :param guest_id: Guest ID to test retrieving guest details
    """
    guest = Guest(connect_dict=get_connect_dict())
    info = guest.retrieve_details_by_id(guest_id)

    assert info, f"Guest ID {guest_id} not found"
    assert "name" in info, f"'name' attribute was returned for ID {guest_id}"
    assert "appearances" in info, f"'appearances' was not returned for ID {guest_id}"


@pytest.mark.parametrize("guest_slug", ["tom-hanks"])
def test_guest_guest_retrieve_details_by_slug(guest_slug: str):
    """Testing for :py:meth:`wwdtm.guest.Guest.retrieve_details_by_slug`

    :param guest_slug: Guest slug string to test retrieving guest details
    """
    guest = Guest(connect_dict=get_connect_dict())
    info = guest.retrieve_details_by_slug(guest_slug)

    assert info, f"Guest slug {guest_slug} not found"
    assert "name" in info, f"'name' was not returned for slug {guest_slug}"
    assert "appearances" in info, f"'appearances' was not returned for slug {guest_slug}"
