# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Supplemental Show Information
Retrieval Functions
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional

from mysql.connector import connect
from slugify import slugify
from wwdtm.show.utility import ShowUtility
from wwdtm.location.location import LocationUtility
from wwdtm.validation import valid_int_id


class ShowInfo:
    """This class contains functions that retrieve show supplemental
    show information, including panelist, guest and Bluff the Listener
    information from a copy of the Wait Wait Stats database.

    :param connect_dict: Dictionary containing database connection
        settings as required by mysql.connector.connect
    :param database_connection: mysql.connector.connect database
        connection
    """

    def __init__(self,
                 connect_dict: Optional[Dict[str, Any]] = None,
                 database_connection: Optional[connect] = None):
        """Class initialization method.
        """
        if connect_dict:
            self.connect_dict = connect_dict
            self.database_connection = connect(**connect_dict)
        elif database_connection:
            if not database_connection.is_connected():
                database_connection.reconnect()

            self.database_connection = database_connection

        self.utility = ShowUtility(database_connection=self.database_connection)
        self.loc_util = LocationUtility(database_connection=self.database_connection)

    @lru_cache(typed=True)
    def retrieve_bluff_info_by_id(self, show_id: int) -> Dict[str, Any]:
        """Returns a dictionary containing Bluff the Listener information
        for the requested show ID.

        :param show_id: Show ID
        :return: Dictionary containing correct and chosen Bluff the
            Listener information.
        """
        if not valid_int_id(show_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT blm.chosenbluffpnlid AS id, "
                 "p.panelist AS name, p.panelistslug As slug "
                 "FROM ww_showbluffmap blm "
                 "JOIN ww_shows s ON s.showid = blm.showid "
                 "JOIN ww_panelists p ON "
                 "p.panelistid = blm.chosenbluffpnlid "
                 "WHERE s.showid = %s;")
        cursor.execute(query, (show_id, ))
        chosen_result = cursor.fetchone()

        if chosen_result:
            chosen_bluff_info = {
                "id": chosen_result.id,
                "name": chosen_result.name,
                "slug": chosen_result.slug if chosen_result.slug else slugify(chosen_result.name),
            }
        else:
            chosen_bluff_info = None

        query = ("SELECT blm.correctbluffpnlid AS id, "
                 "p.panelist AS name, p.panelistslug AS slug "
                 "FROM ww_showbluffmap blm "
                 "JOIN ww_shows s ON s.showid = blm.showid "
                 "JOIN ww_panelists p ON "
                 "p.panelistid = blm.correctbluffpnlid "
                 "WHERE s.showid = %s;")
        cursor.execute(query, (show_id, ))
        correct_result = cursor.fetchone()
        cursor.close()

        if correct_result:
            correct_bluff_info = {
                "id": correct_result.id,
                "name": correct_result.name,
                "slug": correct_result.slug if correct_result.slug else slugify(correct_result.name),
            }
        else:
            correct_bluff_info = None

        return {
            "chosen_panelist": chosen_bluff_info,
            "correct_panelist": correct_bluff_info,
        }

    def retrieve_core_info_by_id(self, show_id: int) -> Dict[str, Any]:
        """Returns a dictionary with core information for the requested
        show ID.

        :param show_ids: List of show IDs
        :return: Dictionary containing host, scorekeeper, location,
            description and notes. If show core information could not be
            retrieved, an empty dictionary will be returned.
        """
        if not valid_int_id(show_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT s.showid AS show_id, s.showdate AS date, "
                 "s.bestof AS best_of, s.repeatshowid AS repeat_show_id, "
                 "l.locationid AS location_id, l.city, l.state, "
                 "l.venue, l.locationslug AS location_slug, h.hostid AS host_id, "
                 "h.host, h.hostslug AS host_slug, hm.guest as host_guest, "
                 "sk.scorekeeperid AS scorekeeper_id, sk.scorekeeper, "
                 "sk.scorekeeperslug AS scorekeeper_slug, "
                 "skm.guest AS scorekeeper_guest, "
                 "skm.description AS scorekeeper_description, "
                 "sd.showdescription AS show_description, "
                 "sn.shownotes AS show_notes "
                 "FROM ww_shows s "
                 "JOIN ww_showlocationmap lm ON lm.showid = s.showid "
                 "JOIN ww_locations l ON l.locationid = lm.locationid "
                 "JOIN ww_showhostmap hm ON hm.showid = s.showid "
                 "JOIN ww_hosts h ON h.hostid = hm.hostid "
                 "JOIN ww_showskmap skm ON skm.showid = s.showid "
                 "JOIN ww_scorekeepers sk ON "
                 "sk.scorekeeperid = skm.scorekeeperid "
                 "JOIN ww_showdescriptions sd ON sd.showid = s.showid "
                 "JOIN ww_shownotes sn ON sn.showid = s.showid "
                 "WHERE s.showid = %s "
                 "ORDER BY s.showdate ASC;")
        cursor.execute(query, (show_id, ))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return {}

        location_info = {
            "id": result.location_id,
            "slug": result.location_slug,
            "city": result.city,
            "state": result.state,
            "venue": result.venue,
        }

        if not result.location_slug:
            location_info["slug"] = self.loc_util.slugify_location(location_id=result.location_id,
                                                                   venue=result.venue,
                                                                   city=result.city,
                                                                   state=result.state)

        host_info = {
            "id": result.host_id,
            "name": result.host,
            "slug": result.host_slug if result.host_slug else slugify(result.host),
            "guest": bool(result.host_guest),
        }

        scorekeeper_info = {
            "id": result.scorekeeper_id,
            "name": result.scorekeeper,
            "slug": result.scorekeeper_slug if result.scorekeeper_slug else slugify(result.scorekeeper),
            "guest": bool(result.scorekeeper_guest),
            "description": result.scorekeeper_description if result.scorekeeper_description else None,
        }

        if result.show_description:
            description = str(result.show_description).strip()
        else:
            description = None

        if result.show_notes:
            notes = str(result.show_notes).strip()
        else:
            notes = None

        show_info = {
            "id": result.show_id,
            "date": result.date.isoformat(),
            "best_of": bool(result.best_of),
            "repeat_show": bool(result.repeat_show_id),
            "original_show_id": None,
            "original_show_date": None,
            "description": description,
            "notes": notes,
            "location": location_info,
            "host": host_info,
            "scorekeeper": scorekeeper_info,
        }

        repeat_show_id = result.repeat_show_id
        if repeat_show_id:
            original_date = self.utility.convert_id_to_date(repeat_show_id)
            show_info["original_show_id"] = repeat_show_id
            show_info["original_show_date"] = original_date
        else:
            show_info.pop("original_show_id", None)
            show_info.pop("original_show_date", None)

        return show_info

    @lru_cache(typed=True)
    def retrieve_guest_info_by_id(self, show_id: int) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing Not My Job
        guest information for the requested show ID.

        :param show_id: Show ID
        :return: Dictionary containing Not My Job guest information. If
            Not My Job information could not be retrieved, an empty list
            will be returned.
        """
        if not valid_int_id(show_id):
            return []

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT gm.guestid AS id, g.guest AS name, "
                 "g.guestslug AS slug, gm.guestscore AS score, "
                 "gm.exception AS score_exception "
                 "FROM ww_showguestmap gm "
                 "JOIN ww_guests g on g.guestid = gm.guestid "
                 "JOIN ww_shows s on s.showid = gm.showid "
                 "WHERE gm.showid = %s "
                 "ORDER by gm.showguestmapid ASC;")
        cursor.execute(query, (show_id, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        guests = []
        for guest in results:
            guests.append({
                "id": guest.id,
                "name": guest.name,
                "slug": guest.slug if guest.slug else slugify(guest.name),
                "score": guest.score if guest.score else None,
                "score_exception": bool(guest.score_exception),
            })

        return guests

    @lru_cache(typed=True)
    def retrieve_panelist_info_by_id(self, show_id: int) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing panelist
        information for the requested show ID.

        :param show_id: Show ID
        :return: List of panelists with corresponding scores and
            ranking information. If panelist information could not be
            retrieved, an empty list will be returned.
        """
        if not valid_int_id(show_id):
            return []

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT pm.panelistid AS id, p.panelist AS name, "
                 "p.panelistslug AS slug, "
                 "pm.panelistlrndstart AS start, "
                 "pm.panelistlrndcorrect AS correct, "
                 "pm.panelistscore AS score, pm.showpnlrank AS rank "
                 "FROM ww_showpnlmap pm "
                 "JOIN ww_panelists p on p.panelistid = pm.panelistid "
                 "WHERE pm.showid = %s "
                 "ORDER by pm.panelistscore DESC, pm.showpnlmapid ASC;")
        cursor.execute(query, (show_id, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        panelists = []
        for row in results:
            panelists.append({
                "id": row.id,
                "name": row.name,
                "slug": row.slug if row.slug else slugify(row.name),
                "lightning_round_start": row.start,
                "lightning_round_correct": row.correct,
                "score": row.score if row.score else None,
                "rank": row.rank if row.rank else None,
            })

        return panelists
