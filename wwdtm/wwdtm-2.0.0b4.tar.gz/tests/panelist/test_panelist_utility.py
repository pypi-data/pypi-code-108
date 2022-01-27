# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object: :py:class:`wwdtm.panelist.PanelistUtility`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.panelist import PanelistUtility


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
def test_panelist_utility_convert_id_to_slug(panelist_id: int):
    """Testing for :py:meth:`wwdtm.panelist.PanelistUtility.convert_id_to_slug`

    :param panelist_id: Panelist ID to test converting into panelist
        slug string
    """
    utility = PanelistUtility(get_connect_dict())
    slug = utility.convert_id_to_slug(panelist_id)

    assert slug, f"Panelist slug for ID {panelist_id} was not found"
    assert isinstance(slug, str), f"Invalid value returned for ID {panelist_id}"


@pytest.mark.parametrize("panelist_id", [-1])
def test_panelist_utility_convert_invalid_id_to_slug(panelist_id: int):
    """Negative testing for :py:meth:`wwdtm.panelist.PanelistUtility.convert_id_to_slug`

    :param panelist_id: Panelist ID to test failing to convert into
        panelist slug string
    """
    utility = PanelistUtility(get_connect_dict())
    slug = utility.convert_id_to_slug(panelist_id)

    assert not slug, f"Panelist slug for ID {panelist_id} was found"


@pytest.mark.parametrize("panelist_slug", ["faith-salie"])
def test_panelist_utility_convert_slug_to_id(panelist_slug: str):
    """Testing for :py:meth:`wwdtm.panelist.PanelistUtility.convert_slug_to_id`

    :param panelist_slug: Panelist slug string to test converting into
        panelist ID
    """
    utility = PanelistUtility(get_connect_dict())
    id_ = utility.convert_slug_to_id(panelist_slug)

    assert id_, f"Panelist ID for slug {panelist_slug} was not found"
    assert isinstance(id_, int), f"Invalid value returned for slug {panelist_slug}"


@pytest.mark.parametrize("panelist_slug", ["faith-sale"])
def test_panelist_utility_convert_invalid_slug_to_id(panelist_slug: str):
    """Negative testing for :py:meth:`wwdtm.panelist.PanelistUtility.convert_slug_to_id`

    :param panelist_slug: Panelist slug string to test failing to
        convert into panelist ID
    """
    utility = PanelistUtility(get_connect_dict())
    id_ = utility.convert_slug_to_id(panelist_slug)

    assert not id_, f"Panelist ID for slug {panelist_slug} was found"


@pytest.mark.parametrize("panelist_id", [14])
def test_panelist_utility_id_exists(panelist_id: int):
    """Testing for :py:meth:`wwdtm.panelist.PanelistUtility.id_exists`

    :param panelist_id: Panelist ID to test if a panelist exists
    """
    utility = PanelistUtility(get_connect_dict())
    result = utility.id_exists(panelist_id)

    assert result, f"Panelist ID {panelist_id} does not exist"


@pytest.mark.parametrize("panelist_id", [-1])
def test_panelist_utility_id_not_exists(panelist_id: int):
    """Negative testing for :py:meth:`wwdtm.panelist.PanelistUtility.id_exists`

    :param panelist_id: Panelist ID to test if a panelist does not exist
    """
    utility = PanelistUtility(get_connect_dict())
    result = utility.id_exists(panelist_id)

    assert not result, f"Panelist ID {panelist_id} exists"


@pytest.mark.parametrize("panelist_slug", ["faith-salie"])
def test_panelist_utility_slug_exists(panelist_slug: str):
    """Testing for :py:meth:`wwdtm.panelist.PanelistUtility.slug_exists`

    :param panelist_slug: Panelist slug string to test if a panelist
        exists
    """
    utility = PanelistUtility(get_connect_dict())
    result = utility.slug_exists(panelist_slug)

    assert result, f"Panelist slug {panelist_slug} does not exist"


@pytest.mark.parametrize("panelist_slug", ["faith-sale"])
def test_panelist_utility_slug_not_exists(panelist_slug: str):
    """Negative testing for :py:meth:`wwdtm.panelist.PanelistUtility.slug_exists`

    :param panelist_slug: Panelist slug string to test if a panelist
        does not exist
    """
    utility = PanelistUtility(get_connect_dict())
    result = utility.slug_exists(panelist_slug)

    assert not result, f"Panelist slug {panelist_slug} exists"
