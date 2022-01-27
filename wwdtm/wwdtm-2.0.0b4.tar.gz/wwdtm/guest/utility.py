# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Guest Data Utility Functions
"""
from functools import lru_cache
from typing import Any, Dict, Optional

from mysql.connector import connect
from wwdtm.validation import valid_int_id


class GuestUtility:
    """This class contains supporting functions used to check whether
    a Guest ID or slug string exists or to convert an ID to a slug
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
    def convert_id_to_slug(self, guest_id: int) -> Optional[str]:
        """Converts a guest's ID to the matching guest slug string.

        :param guest_id: Guest ID
        :return: Guest slug string, if a match is found
        """
        if not valid_int_id(guest_id):
            return None

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT guestslug FROM ww_guests "
                 "WHERE guestid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (guest_id, ))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]

        return None

    @lru_cache(typed=True)
    def convert_slug_to_id(self, guest_slug: str) -> Optional[int]:
        """Converts a guest's slug string to the matching guest ID, if
        a match is found. If no match is found, None is returned.

        :param guest_slug: Guest slug string
        :return: Guest ID, if a match is found
        """
        try:
            slug = guest_slug.strip()
            if not slug:
                return None
        except ValueError:
            return None

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT guestid FROM ww_guests "
                 "WHERE guestslug = %s "
                 "LIMIT 1;")
        cursor.execute(query, (slug, ))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]

        return None

    @lru_cache(typed=True)
    def id_exists(self, guest_id: int) -> bool:
        """Checks to see if a guest ID exists.

        :param guest_id: Guest ID
        :return: True or False, based on whether the guest ID exists
        """
        if not valid_int_id(guest_id):
            return False

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT guestid FROM ww_guests "
                 "WHERE guestid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (guest_id, ))
        result = cursor.fetchone()
        cursor.close()

        return bool(result)

    @lru_cache(typed=True)
    def slug_exists(self, guest_slug: str) -> bool:
        """Checks to see if a guest slug string exists.

        :param guest_slug: Guest slug string
        :return: True or False, based on whether the guest slug string
            exists
        """
        try:
            slug = guest_slug.strip()
            if not slug:
                return False
        except ValueError:
            return False

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT guestslug FROM ww_guests "
                 "WHERE guestslug = %s "
                 "LIMIT 1;")
        cursor.execute(query, (slug, ))
        result = cursor.fetchone()
        cursor.close()

        return bool(result)
