# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Location Recordings Retrieval Functions
"""
from functools import lru_cache
from typing import Any, Dict, Optional

from mysql.connector import connect
from wwdtm.location.utility import LocationUtility
from wwdtm.validation import valid_int_id


class LocationRecordings:
    """This class contains functions that retrieve location recordings
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

        self.utility = LocationUtility(database_connection=self.database_connection)

    @lru_cache(typed=True)
    def retrieve_recordings_by_id(self, location_id: int) -> Dict[str, Any]:
        """Returns a list of dictionary objects containing recording
        information for the requested location ID.

        :param location_id: Location ID
        :return: Dictionary containing recording counts and a list of
            appearances for a location. If location recordings could
            not be retrieved, an empty dictionary is returned.
        """
        if not valid_int_id(location_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT ( "
                 "SELECT COUNT(lm.showid) FROM ww_showlocationmap lm "
                 "JOIN ww_shows s ON s.showid = lm.showid "
                 "WHERE s.bestof = 0 AND s.repeatshowid IS NULL AND "
                 "lm.locationid = %s ) AS regular_shows, ( "
                 "SELECT COUNT(lm.showid) FROM ww_showlocationmap lm "
                 "JOIN ww_shows s ON s.showid = lm.showid "
                 "WHERE lm.locationid = %s ) AS all_shows;")
        cursor.execute(query, (location_id, location_id, ))
        result = cursor.fetchone()

        recording_counts = {
            "regular_shows": result.regular_shows,
            "all_shows": result.all_shows,
        }

        query = ("SELECT lm.showid AS show_id, s.showdate AS date, "
                 "s.bestof AS best_of, s.repeatshowid AS repeat_show_id "
                 "FROM ww_showlocationmap lm "
                 "JOIN ww_shows s ON s.showid = lm.showid "
                 "WHERE lm.locationid = %s "
                 "ORDER BY s.showdate ASC;")
        cursor.execute(query, (location_id, ))
        results = cursor.fetchall()
        cursor.close()

        if results:
            recordings = []
            for recording in results:
                info = {
                    "show_id": recording.show_id,
                    "date": recording.date.isoformat(),
                    "best_of": bool(recording.best_of),
                    "repeat_show": bool(recording.repeat_show_id),
                }
                recordings.append(info)

            return {
                "count": recording_counts,
                "shows": recordings,
            }
        else:
            return {
                "count": recording_counts,
                "shows": [],
            }

    @lru_cache(typed=True)
    def retrieve_recordings_by_slug(self, location_slug: str) -> Dict[str, Any]:
        """Returns a list of dictionary objects containing recording
        information for the requested location slug string.

        :param location_slug: Location slug string
        :return: Dictionary containing recording counts and a list of
            appearances for a location. If location recordings could
            not be retrieved, an empty dictionary is returned.
        """
        id_ = self.utility.convert_slug_to_id(location_slug)
        if not id_:
            return {}

        return self.retrieve_recordings_by_id(id_)
