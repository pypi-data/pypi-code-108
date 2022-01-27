# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object: :py:class:`wwdtm.guest.GuestAppearances`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.guest import GuestAppearances


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


@pytest.mark.parametrize("guest_id", [976])
def test_guest_appearances_retrieve_appearances_by_id(guest_id: int):
    """Testing for :py:meth:`wwdtm.guest.Appearances.retrieve_appearances_by_id`

    :param guest_id: Guest ID to test retrieving guest appearances
    """
    appearances = GuestAppearances(connect_dict=get_connect_dict())
    appearance = appearances.retrieve_appearances_by_id(guest_id)

    assert "count" in appearance, f"'count' was not returned for ID {guest_id}"
    assert "shows" in appearance, f"'shows' was not returned for ID {guest_id}"


@pytest.mark.parametrize("guest_slug", ["tom-hanks"])
def test_guest_appearances_retrieve_appearances_by_slug(guest_slug: str):
    """Testing for :py:meth:`wwdtm.guest.Appearances.retrieve_appearances_by_slug`

    :param guest_slug: Guest slug string to test retrieving guest appearances
    """
    appearances = GuestAppearances(connect_dict=get_connect_dict())
    appearance = appearances.retrieve_appearances_by_slug(guest_slug)

    assert "count" in appearance, f"'count' was not returned for slug {guest_slug}"
    assert "shows" in appearance, f"'shows' was not returned for slug {guest_slug}"
