# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Testing for object :py:class:`wwdtm.show.ShowInfo`
"""
import json
from typing import Any, Dict, List

import pytest
from wwdtm.show import ShowInfoMultiple


@pytest.mark.skip
def get_connect_dict() -> Dict[str, Any]:
    """Read in database connection settings and return values as a
    dictionary.
    """
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)
        if "database" in config_dict:
            return config_dict["database"]


@pytest.mark.parametrize("show_id", [1083])
def test_show_info_retrieve_bluff_info_all(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowInfoMultiple.retrieve_bluff_info_all`

    :param show_id: Show ID to test retrieving show Bluff the Listener
        information from all shows retrieved
    """
    info = ShowInfoMultiple(connect_dict=get_connect_dict())
    bluffs = info.retrieve_bluff_info_all()

    assert bluffs, ("Bluff the Listener information for all shows could not "
                    "be retrieved")
    assert show_id in bluffs, ("Bluff the Listener information was not "
                               f"returned for show ID {show_id}")

    bluff = bluffs[show_id]
    assert "chosen_panelist" in bluff, ("'chosen_panelist' was not returned with "
                                        f"panelist information for show ID {show_id}")
    assert "correct_panelist" in bluff, ("'correct_panelist' was not returned with "
                                         f"panelist information for show ID {show_id}")


@pytest.mark.parametrize("show_ids", [[1083, 1162]])
def test_show_info_retrieve_bluff_info_by_ids(show_ids: List[int]):
    """Testing for :py:meth:`wwdtm.show.ShowInfoMultiple.retrieve_bluff_info_by_ids`

    :param show_ids: List of show IDs to test retrieving show Bluff the
        Listener information
    """
    info = ShowInfoMultiple(connect_dict=get_connect_dict())
    bluffs = info.retrieve_bluff_info_by_ids(show_ids)

    assert bluffs, (f"Bluff the Listener information for the show IDs {show_ids} "
                    f"could not be retrieved")

    for show_id in show_ids:
        assert show_id in bluffs, ("Bluff the Listener information was not "
                                   f"returned for show ID {show_id}")
        assert "chosen_panelist" in bluffs[show_id], ("'chosen_panelist' was not "
                                                      "returned with panelist "
                                                      "information for show ID "
                                                      f"{show_id}")
        assert "correct_panelist" in bluffs[show_id], ("'correct_panelist' was not "
                                                       "returned with panelist "
                                                       "information for show ID "
                                                       f"{show_id}")


@pytest.mark.parametrize("show_id", [1162])
def test_show_info_retrieve_core_info_all(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowInfoMultiple.retrieve_core_info_all`

    :param show_id: Show ID to test retrieving show core information
        from all shows retrieved
    """
    info = ShowInfoMultiple(connect_dict=get_connect_dict())
    shows = info.retrieve_core_info_all()

    assert shows, "Core information for all shows could not be retrieved"
    assert show_id in shows, (f"Core information for show ID {show_id} "
                              f"could not be retrieved")

    show = shows[show_id]
    assert "id" in show, ("'id' was not returned with core information for "
                          f"show ID {show_id}")
    assert "description" in show, ("'description' was not returned with show "
                                   f"information for show ID {show_id}")


@pytest.mark.parametrize("show_ids", [[1082, 1162]])
def test_show_info_retrieve_core_info_by_ids(show_ids: List[int]):
    """Testing for :py:meth:`wwdtm.show.ShowInfoMultiple.retrieve_core_info_by_ids`

    :param show_id: Show ID to test retrieving show core information
    """
    info = ShowInfoMultiple(connect_dict=get_connect_dict())
    shows = info.retrieve_core_info_by_ids(show_ids)

    assert shows, "Core information all shows could not be retrieved"

    for show_id in show_ids:
        assert show_id in shows, ("Core information could not be retrieved for "
                                  f"show ID {show_id}")
        assert "id" in shows[show_id], ("'id' was not returned with core information "
                                        f"for show ID {show_id}")
        assert "description" in shows[show_id], ("'description' was not returned with "
                                                 f"show information for show ID {show_id}")


@pytest.mark.parametrize("show_id", [1082])
def test_show_info_retrieve_guest_info_all(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowInfoMultiple.retrieve_guest_info_all`

    :param show_id: Show ID to test retrieving show guest information
        for all shows retrieved
    """
    info = ShowInfoMultiple(connect_dict=get_connect_dict())
    shows_guests = info.retrieve_guest_info_all()

    assert shows_guests, "Guest information all shows could not be retrieved"
    assert show_id in shows_guests, ("Guest information could not be retrieved for "
                                     f"show ID {show_id}")

    guests = shows_guests[show_id]
    if guests:
        assert "id" in guests[0], ("'id' was not returned for the first guest "
                                   f"for show ID {show_id}")
        assert "score" in guests[0], ("'score' was not returned for the first "
                                      f"guest for show ID {show_id}")


@pytest.mark.parametrize("show_ids", [[1082, 1162]])
def test_show_info_retrieve_guest_info_by_ids(show_ids: List[int]):
    """Testing for :py:meth:`wwdtm.show.ShowInfoMultiple.retrieve_guest_info_by_ids`

    :param show_ids: List of show IDs to test retrieving show guest
        information
    """
    info = ShowInfoMultiple(connect_dict=get_connect_dict())
    shows_guests = info.retrieve_guest_info_by_ids(show_ids)

    assert shows_guests, (f"Guest information for show IDs {show_ids} could not "
                          "be retrieved")

    for show_id in show_ids:
        assert show_id in shows_guests, (f"Guest information for show ID {show_id} "
                                         "could not be retrieved")

        guests = shows_guests[show_id]
        if guests:
            assert "id" in guests[0], ("'id' was not returned for the first guest "
                                       f"for show ID {show_id}")
            assert "score" in guests[0], ("'score' was not returned for the first "
                                          f"guest for show ID {show_id}")


@pytest.mark.parametrize("show_id", [1082])
def test_show_info_retrieve_panelist_info_all(show_id: int):
    """Testing for :py:meth:`wwdtm.show.ShowInfoMultiple.retrieve_panelist_info_all`

    :param show_id: Show ID to test retrieving show panelist information
        for all shows retrieved
    """
    info = ShowInfoMultiple(connect_dict=get_connect_dict())
    shows_panelists = info.retrieve_panelist_info_all()

    assert shows_panelists, f"Panelist information for all shows could not be retrieved"
    assert show_id in shows_panelists, ("Panelist information could not be retrieved "
                                        f"for show ID {show_id}")

    panelists = shows_panelists[show_id]
    assert "id" in panelists[0], (f"'id' was not returned for the first panelist "
                                  f"for show ID {show_id}")
    assert "score" in panelists[0], (f"'score' was not returned for the first "
                                     f"panelist for show ID {show_id}")


@pytest.mark.parametrize("show_ids", [[1082, 1162]])
def test_show_info_retrieve_panelist_info_by_ids(show_ids: List[int]):
    """Testing for :py:meth:`wwdtm.show.ShowInfoMultiple.retrieve_panelist_info_by_ids`

    :param show_ids: List of show IDs to test retrieving show panelist
        information
    """
    info = ShowInfoMultiple(connect_dict=get_connect_dict())
    shows_panelists = info.retrieve_panelist_info_by_ids(show_ids)

    assert shows_panelists, (f"Panelist information for show IDs {show_ids} could not "
                             "be retrieved")

    for show_id in shows_panelists:
        assert show_id in shows_panelists, ("Panelist information could not be "
                                            f"retrieved for show ID {show_id}")
        panelists = shows_panelists[show_id]
        if panelists:
            assert "id" in panelists[0], (f"'id' was not returned for the first panelist "
                                          f"for show ID {show_id}")
            assert "score" in panelists[0], (f"'score' was not returned for the first "
                                             f"panelist for show ID {show_id}")
