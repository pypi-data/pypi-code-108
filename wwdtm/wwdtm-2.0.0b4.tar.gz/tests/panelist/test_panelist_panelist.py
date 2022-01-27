# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object: :py:class:`wwdtm.panelist.Panelist`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.panelist import Panelist


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


def test_panelist_retrieve_all():
    """Testing for :py:meth:`wwdtm.panelist.Panelist.retrieve_all`
    """
    panelist = Panelist(connect_dict=get_connect_dict())
    panelists = panelist.retrieve_all()

    assert panelists, "No panelists could be retrieved"
    assert "id" in panelists[0], "'id' was not returned for the first list item"


def test_panelist_retrieve_all_details():
    """Testing for :py:meth:`wwdtm.panelist.Panelist.retrieve_all_details`
    """
    panelist = Panelist(connect_dict=get_connect_dict())
    panelists = panelist.retrieve_all_details()

    assert panelists, "No panelists could be retrieved"
    assert "id" in panelists[0], "'id' was not returned for first list item"
    assert "appearances" in panelists[0], ("'appearances' was not returned for "
                                           "the first list item")


def test_panelist_retrieve_all_ids():
    """Testing for :py:meth:`wwdtm.panelist.Panelist.retrieve_all_ids`
    """
    panelist = Panelist(connect_dict=get_connect_dict())
    ids = panelist.retrieve_all_ids()

    assert ids, "No panelist IDs could be retrieved"


def test_panelist_retrieve_all_slugs():
    """Testing for :py:meth:`wwdtm.panelist.Panelist.retrieve_all_slugs`
    """
    panelist = Panelist(connect_dict=get_connect_dict())
    slugs = panelist.retrieve_all_slugs()

    assert slugs, "No panelist slug strings could be retrieved"


@pytest.mark.parametrize("panelist_id", [14])
def test_panelist_retrieve_by_id(panelist_id: int):
    """Testing for :py:meth:`wwdtm.panelist.Panelist.retrieve_by_id`

    :param panelist_id: Panelist ID to test retrieving panelist
        information
    """
    panelist = Panelist(connect_dict=get_connect_dict())
    info = panelist.retrieve_by_id(panelist_id)

    assert info, f"Panelist ID {panelist_id} not found"
    assert "name" in info, f"'name' was not returned for ID {panelist_id}"


@pytest.mark.parametrize("panelist_id", [14])
def test_panelist_retrieve_details_by_id(panelist_id: int):
    """Testing for :py:meth:`wwdtm.panelist.Panelist.retrieve_details_by_id`

    :param panelist_id: Panelist ID to test retrieving panelist details
    """
    panelist = Panelist(connect_dict=get_connect_dict())
    info = panelist.retrieve_details_by_id(panelist_id)

    assert info, f"Panelist ID {panelist_id} not found"
    assert "name" in info, f"'name' was not returned for ID {panelist_id}"
    assert "appearances" in info, f"'appearances' was not returned for ID {panelist_id}"


@pytest.mark.parametrize("panelist_slug", ["luke-burbank", "drew-carey"])
def test_panelist_retrieve_by_slug(panelist_slug: str):
    """Testing for :py:meth:`wwdtm.panelist.Panelist.retrieve_by_slug`

    :param panelist_slug: Panelist slug string to test retrieving
        panelist information
    """
    panelist = Panelist(connect_dict=get_connect_dict())
    info = panelist.retrieve_by_slug(panelist_slug)

    assert info, f"Panelist slug {panelist_slug} not found"
    assert "name" in info, f"'name' was not returned for slug {panelist_slug}"


@pytest.mark.parametrize("panelist_slug", ["luke-burbank"])
def test_panelist_retrieve_details_by_slug(panelist_slug: str):
    """Testing for :py:meth:`wwdtm.panelist.Panelist.retrieve_details_by_slug`

    :param panelist_slug: Panelist slug string to test retrieving
        panelist details
    """
    panelist = Panelist(connect_dict=get_connect_dict())
    info = panelist.retrieve_details_by_slug(panelist_slug)

    assert info, f"Panelist slug {panelist_slug} not found"
    assert "name" in info, f"'name' was not returned for slug {panelist_slug}"
    assert "appearances" in info, f"'appearances' was not returned for slug {panelist_slug}"
