# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Scorekeeper Appearance Retrieval
Functions
"""
from functools import lru_cache
from typing import Any, Dict, Optional

from mysql.connector import connect
from wwdtm.scorekeeper.utility import ScorekeeperUtility
from wwdtm.validation import valid_int_id


class ScorekeeperAppearances:
    """This class contains functions that retrieve scorekeeper
    appearance information from a copy of the Wait Wait Stats database.

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

        self.utility = ScorekeeperUtility(database_connection=self.database_connection)

    @lru_cache(typed=True)
    def retrieve_appearances_by_id(self, scorekeeper_id: int) -> Dict[str, Any]:
        """Returns a list of dictionary objects containing appearance
        information for the requested scorekeeper ID.

        :param scorekeeper_id: Scorekeeper ID
        :return: Dictionary containing appearance counts and list of
            appearances for a scorekeeper. If scorekeeper appearances
            could not be retrieved, an empty dictionary would be
            returned.
        """
        if not valid_int_id(scorekeeper_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT ( "
                 "SELECT COUNT(skm.showid) FROM ww_showskmap skm "
                 "JOIN ww_shows s ON s.showid = skm.showid "
                 "WHERE s.bestof = 0 AND s.repeatshowid IS NULL AND "
                 "skm.scorekeeperid = %s ) AS regular_shows, ( "
                 "SELECT COUNT(skm.showid) FROM ww_showskmap skm "
                 "JOIN ww_shows s ON s.showid = skm.showid "
                 "WHERE skm.scorekeeperid = %s ) AS all_shows;")
        cursor.execute(query, (scorekeeper_id, scorekeeper_id, ))
        result = cursor.fetchone()

        if result:
            appearance_counts = {
                "regular_shows": result.regular_shows,
                "all_shows": result.all_shows,
            }
        else:
            appearance_counts = {
                "regular_shows": 0,
                "all_shows": 0,
            }

        query = ("SELECT skm.showid AS show_id, s.showdate AS date, "
                 "s.bestof AS best_of, s.repeatshowid AS repeat_show_id, "
                 "skm.guest, skm.description "
                 "FROM ww_showskmap skm "
                 "JOIN ww_scorekeepers sk ON sk.scorekeeperid = skm.scorekeeperid "
                 "JOIN ww_shows s ON s.showid = skm.showid "
                 "WHERE sk.scorekeeperid = %s "
                 "ORDER BY s.showdate ASC;")
        cursor.execute(query, (scorekeeper_id, ))
        results = cursor.fetchall()
        cursor.close()

        if results:
            appearances = []
            for appearance in results:
                info = {
                    "show_id": appearance.show_id,
                    "date": appearance.date.isoformat(),
                    "best_of": bool(appearance.best_of),
                    "repeat_show": bool(appearance.repeat_show_id),
                    "guest": bool(appearance.guest),
                    "description": appearance.description,
                }
                appearances.append(info)

            return {
                "count": appearance_counts,
                "shows": appearances,
            }

        else:
            return {
                "count": appearance_counts,
                "shows": [],
            }

    @lru_cache(typed=True)
    def retrieve_appearances_by_slug(self, scorekeeper_slug: str) -> Dict[str, Any]:
        """Returns a list of dictionary objects containing appearance
        information for the requested scorekeeper ID.

        :param scorekeeper_slug: Scorekeeper slug string
        :return: Dictionary containing appearance counts and list of
            appearances for a scorekeeper. If scorekeeper appearances
            could not be retrieved, an empty dictionary would be
            returned.
        """
        id_ = self.utility.convert_slug_to_id(scorekeeper_slug)
        if not id_:
            return {}

        return self.retrieve_appearances_by_id(id_)
