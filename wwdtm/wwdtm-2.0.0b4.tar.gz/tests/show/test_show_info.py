# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object :py:class:`wwdtm.show.ShowInfo`
"""
import json
from typing import Any, Dict

import pytest
from wwdtm.show import ShowInfo


@pytest.mark.skip
def get_connect_dict() -> Dict[str, Any]:
    """Read in database connection settings and return values as a
    dictionary.
    """
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
        if "database" in config_dict:
            return config_dict["database"]


@pytest.mark.parametrize("show_id", [1162])
def test_show_info_retrieve_bluff_info_by_id(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowInfo.retrieve_bluff_info_by_id`

    :param show_id: Show ID to test retrieving show Bluff the Listener
        information
    """
    info = ShowInfo(connect_dict=get_connect_dict())
    bluff = info.retrieve_bluff_info_by_id(show_id)

    assert bluff, (f"Bluff the Listener information for show ID {show_id} could "
                   f"not be retrieved")
    assert "chosen_panelist" in bluff, (f"'chosen_panelist' was not returned with "
                                        f"panelist information for show ID {show_id}")
    assert "correct_panelist" in bluff, (f"'correct_panelist' was not returned with "
                                         f"panelist information for show ID {show_id}")


@pytest.mark.parametrize("show_id", [1162])
def test_show_info_retrieve_core_info_by_id(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowInfo.retrieve_core_info_by_id`

    :param show_id: Show ID to test retrieving show core information
    """
    info = ShowInfo(connect_dict=get_connect_dict())
    show = info.retrieve_core_info_by_id(show_id)

    assert show, f"Core information for show ID {show_id} could not be retrieved"

    assert "id" in show, (f"'id' was not returned with core information for "
                          f"show ID {show_id}")
    assert "description" in show, (f"'description' was not returned with show "
                                   f"information for show ID {show_id}")


@pytest.mark.parametrize("show_id", [1162])
def test_show_info_retrieve_guest_info_by_id(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowInfo.retrieve_guest_info_by_id`

    :param show_id: Show ID to test retrieving show guest information
    """
    info = ShowInfo(connect_dict=get_connect_dict())
    guests = info.retrieve_guest_info_by_id(show_id)

    assert guests, f"Guest information for show ID {show_id} could not be retrieved"
    assert "id" in guests[0], (f"'id' was not returned for the first guest for "
                               f"show ID {show_id}")
    assert "score" in guests[0], (f"'score' was not returned for the first "
                                  f"guest for show ID {show_id}")


@pytest.mark.parametrize("show_id", [1162])
def test_show_info_retrieve_panelist_info_by_id(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowInfo.retrieve_panelist_info_by_id`

    :param show_id: Show ID to test retrieving show panelist information
    """
    info = ShowInfo(connect_dict=get_connect_dict())
    panelists = info.retrieve_panelist_info_by_id(show_id)

    assert panelists, (f"Panelist information for show ID {show_id} could not "
                       "be retrieved")
    assert "id" in panelists[0], (f"'id' was not returned for the first panelist "
                                  f"for show ID {show_id}")
    assert "score" in panelists[0], (f"'score' was not returned for the first "
                                     f"panelist for show ID {show_id}")
