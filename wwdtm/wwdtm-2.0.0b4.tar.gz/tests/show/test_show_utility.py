# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object :py:class:`wwdtm.show.ShowUtility`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.show import ShowUtility


@pytest.mark.skip
def get_connect_dict() -> Dict[str, Any]:
    """Read in database connection settings and return values as a
    dictionary.
    """
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
        if "database" in config_dict:
            return config_dict["database"]


@pytest.mark.parametrize("year, month, day", [(2018, 10, 27)])
def test_show_utility_convert_date_to_id(year: int,
                                         month: int,
                                         day: int):
    """Testing for :py:meth:`wwdtm.show.ShowUtility.convert_date_to_id`

    :param year: Four digit year to test converting into show ID
    :param month: One or two digit month to test converting into show ID
    :param day: One or two digit day to test converting into show ID
    """
    utility = ShowUtility(connect_dict=get_connect_dict())
    id_ = utility.convert_date_to_id(year, month, day)

    assert id_, f"Show ID for date {year:04d}-{month:02d}-{day:02d} not found"
    assert isinstance(id_, int), (f"Invalid value returned for date "
                                  f"{year:04d}-{month:02d}-{day:02d}")


@pytest.mark.parametrize("year, month, day", [(2018, 10, 26)])
def test_show_utility_convert_invalid_date_to_id(year: int,
                                                 month: int,
                                                 day: int):
    """Negative testing for :py:meth:`wwdtm.show.ShowUtility.convert_date_to_id`

    :param year: Four digit year to test failing to convert into show ID
    :param month: One or two digit month to test failing to convert
        into show ID
    :param day: One or two digit day to test failing to convert into
        show ID
    """
    utility = ShowUtility(connect_dict=get_connect_dict())
    id_ = utility.convert_date_to_id(year, month, day)

    assert not id_, f"Show ID for date {year:04d}-{month:02d}-{day:02d} was found"


@pytest.mark.parametrize("show_id", [1162])
def test_show_utility_convert_id_to_date(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowUtility.convert_id_to_date`

    :param show_id: Show ID to test converting into show date
    """
    utility = ShowUtility(connect_dict=get_connect_dict())
    date = utility.convert_id_to_date(show_id)

    assert date, f"Show date for ID {show_id} was not found"
    assert isinstance(date, str), f"Invalid value returned for ID {show_id}"


@pytest.mark.parametrize("show_id", [-1])
def test_show_utility_convert_invalid_id_to_date(show_id: int):
    """Negative testing for :py:meth:`wwdtm.show.ShowUtility.convert_id_to_date`

    :param show_id: Show ID to test failing to convert into show date
    """
    utility = ShowUtility(connect_dict=get_connect_dict())
    date = utility.convert_id_to_date(show_id)

    assert not date, f"Show date for ID {show_id} was found"


@pytest.mark.parametrize("year, month, day", [(2020, 4, 25)])
def test_show_utility_date_exists(year: int,
                                  month: int,
                                  day: int):
    """Testing for :py:meth:`wwdtm.show.ShowUtility.date_exists`

    :param year: Four digit year to test if a show exists
    :param month: One or two digit month to test if a show exists
    :param day: One or two digit day to test if a show exists
    """
    utility = ShowUtility(connect_dict=get_connect_dict())
    result = utility.date_exists(year, month, day)

    assert result, f"Show date {year:04d}-{month:02d}-{day:02d} was not found"


@pytest.mark.parametrize("year, month, day", [(2020, 4, 24)])
def test_show_utility_date_not_exists(year: int,
                                      month: int,
                                      day: int):
    """Negative testing for :py:meth:`wwdtm.show.ShowUtility.date_exists`

    :param year: Four digit year to test if a show does not exist
    :param month: One or two digit month to test if a show does not
        exist
    :param day: One or two digit day to test if a show does not exist
    """
    utility = ShowUtility(connect_dict=get_connect_dict())
    result = utility.date_exists(year, month, day)

    assert not result, f"Show date {year:04d}-{month:02d}-{day:02d} was found"


@pytest.mark.parametrize("show_id", [1162])
def test_show_utility_id_exists(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowUtility.id_exists`

    :param show_id: Show ID to test if a show exists
    """
    utility = ShowUtility(connect_dict=get_connect_dict())
    result = utility.id_exists(show_id)

    assert result, f"Show ID {show_id} was not found"


@pytest.mark.parametrize("show_id", [-1])
def test_show_utility_id_not_exists(show_id: int):
    """Negative testing for :py:meth:`wwdtm.show.ShowUtility.id_exists`

    :param show_id: Show ID to test if a show does not exist
    """
    utility = ShowUtility(connect_dict=get_connect_dict())
    result = utility.id_exists(show_id)

    assert not result, f"Show ID {show_id} was found"
