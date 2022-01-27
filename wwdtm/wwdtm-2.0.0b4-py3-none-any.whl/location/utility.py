# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Location Data Utility Functions
"""
from functools import lru_cache
from typing import Any, Dict, Optional

from mysql.connector import connect
from slugify import slugify
from wwdtm.validation import valid_int_id


class LocationUtility:
    """This class contains supporting functions used to check whether
    a Location ID or slug string exists or to convert an ID to a slug
    string, or vice versa.

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

    @lru_cache(typed=True)
    def convert_id_to_slug(self, location_id: int) -> Optional[str]:
        """Converts a location's ID to the matching location slug
        string value.

        :param location_id: Location ID
        :return: Location slug string, if a match is found
        """
        if not valid_int_id(location_id):
            return None

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT locationslug FROM ww_locations "
                 "WHERE locationid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (location_id, ))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]

        return None

    @lru_cache(typed=True)
    def convert_slug_to_id(self, location_slug: str) -> Optional[int]:
        """Converts a location's slug string to the matching location
        ID value.

        :param location_slug: Location slug string
        :return: Location ID, if a match is found
        """
        try:
            slug = location_slug.strip()
            if not slug:
                return None
        except ValueError:
            return None

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT locationid FROM ww_locations "
                 "WHERE locationslug = %s "
                 "LIMIT 1;")
        cursor.execute(query, (slug, ))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]

        return None

    @lru_cache(typed=True)
    def id_exists(self, location_id: int) -> bool:
        """Checks to see if a location ID exists.

        :param location_id: Location ID
        :return: True or False, based on whether the location ID exists
        """
        if not valid_int_id(location_id):
            return False

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT locationid FROM ww_locations "
                 "WHERE locationid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (location_id, ))
        result = cursor.fetchone()
        cursor.close()

        return bool(result)

    @lru_cache(typed=True)
    def slug_exists(self, location_slug: str) -> bool:
        """Checks to see if a location slug string exists.

        :param location_slug: Location slug string
        :return: True or False, based on whether the location slug
            string exists
        """
        try:
            slug = location_slug.strip()
            if not slug:
                return False
        except ValueError:
            return False

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT locationslug FROM ww_locations "
                 "WHERE locationslug = %s "
                 "LIMIT 1;")
        cursor.execute(query, (slug, ))
        result = cursor.fetchone()
        cursor.close()

        return bool(result)

    @staticmethod
    def slugify_location(location_id: Optional[int] = None,
                         venue: Optional[str] = None,
                         city: Optional[str] = None,
                         state: Optional[str] = None
                         ) -> str:
        """Generates a slug string based on the location's venue name,
        city, state and/or location ID.

        :param location_id: Location ID
        :param venue: Location venue name
        :param city: City where the location venue is located
        :param state: State where the location venue is located
        :return: Location slug string
        :raises: ValueError
        """
        if venue and city and state:
            return slugify(f"{venue} {city} {state}")
        elif venue and city and not state:
            return slugify(f"{venue} {city}")
        elif location_id and venue and (not city and not state):
            return slugify(f"{id}-{venue}")
        elif location_id and city and state and not venue:
            return slugify(f"{id} {city} {state}")
        elif location_id:
            return f"location-{location_id}"
        else:
            raise ValueError("Invalid location information provided")
