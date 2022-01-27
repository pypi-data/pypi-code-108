# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object: :py:class:`wwdtm.panelist.PanelistAppearances`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.panelist import PanelistAppearances


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


@pytest.mark.parametrize("panelist_id", [14])
def test_panelist_appearances_retrieve_appearances_by_id(panelist_id: int):
    """Testing for :py:meth:`wwdtm.panelist.PanelistAppearances.retrieve_appearances_by_id`

    :param panelist_id: Panelist ID to test retrieving panelist
        appearances
    """
    appearances = PanelistAppearances(connect_dict=get_connect_dict())
    appearance = appearances.retrieve_appearances_by_id(panelist_id)

    assert "count" in appearance, f"'count' was not returned for ID {panelist_id}"
    assert "shows" in appearance, f"'shows' was not returned for ID {panelist_id}"


@pytest.mark.parametrize("panelist_slug", ["luke-burbank"])
def test_panelist_appearances_retrieve_appearances_by_slug(panelist_slug: str):
    """Testing for :py:meth:`wwdtm.panelist.PanelistAppearances.retrieve_appearances_by_slug`

    :param panelist_slug: Panelist slug string to test retrieving
        panelist appearances
    """
    appearances = PanelistAppearances(connect_dict=get_connect_dict())
    appearance = appearances.retrieve_appearances_by_slug(panelist_slug)

    assert "count" in appearance, f"'count' was not returned for slug {panelist_slug}"
    assert "shows" in appearance, f"'shows' was not returned for slug {panelist_slug}"


@pytest.mark.parametrize("panelist_id", [14])
def test_panelist_appearances_retrieve_yearly_appearances_by_id(panelist_id: int):
    """Testing for :py:meth:`wwdtm.panelist.PanelistAppearances.retrieve_yearly_appearances_by_id`

    :param panelist_id: Panelist ID to test retrieving a panelist's
        appearances
    """
    appearances = PanelistAppearances(connect_dict=get_connect_dict())
    breakdown = appearances.retrieve_yearly_appearances_by_id(panelist_id)

    assert breakdown, f"No appearance information returned for ID {panelist_id}"


@pytest.mark.parametrize("panelist_slug", ["luke-burbank"])
def test_panelist_appearances_retrieve_yearly_appearances_by_slug(panelist_slug: str):
    """Testing for :py:meth:`wwdtm.panelist.PanelistAppearances.retrieve_yearly_appearances_by_slug`

    :param panelist_slug: Panelist slug string to test retrieving
        panelist appearances
    """
    appearances = PanelistAppearances(connect_dict=get_connect_dict())
    breakdown = appearances.retrieve_yearly_appearances_by_slug(panelist_slug)

    assert breakdown, f"No appearance information returned for slug {panelist_slug}"
