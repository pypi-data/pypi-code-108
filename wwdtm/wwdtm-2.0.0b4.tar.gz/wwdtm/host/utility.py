# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Host Data Utility Functions
"""
from functools import lru_cache
from typing import Any, Dict, Optional

from mysql.connector import connect
from wwdtm.validation import valid_int_id


class HostUtility:
    """This class contains supporting functions used to check whether
    a host ID or slug string exists or to convert an ID to a slug
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
    def convert_id_to_slug(self, host_id: int) -> Optional[str]:
        """Converts a host's ID to the matching host slug string value.

        :param host_id: Host ID
        :return: Host slug string, if a match is found
        """
        if not valid_int_id(host_id):
            return None

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT hostslug FROM ww_hosts "
                 "WHERE hostid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (host_id, ))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]

        return None

    @lru_cache(typed=True)
    def convert_slug_to_id(self, host_slug: str) -> Optional[int]:
        """Converts a host's slug string to the matching host ID value.

        :param host_slug: Host slug string
        :return: Host ID, if a match is found
        """
        try:
            slug = host_slug.strip()
            if not slug:
                return None
        except ValueError:
            return None

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT hostid FROM ww_hosts "
                 "WHERE hostslug = %s "
                 "LIMIT 1;")
        cursor.execute(query, (slug, ))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]

        return None

    @lru_cache(typed=True)
    def id_exists(self, host_id: int) -> bool:
        """Checks to see if a host ID exists.

        :param host_id: Host ID
        :return: True or False, based on whether the host ID exists
        """
        if not valid_int_id(host_id):
            return False

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT hostid FROM ww_hosts "
                 "WHERE hostid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (host_id, ))
        result = cursor.fetchone()
        cursor.close()

        return bool(result)

    @lru_cache(typed=True)
    def slug_exists(self, host_slug: str) -> bool:
        """Checks to see if a host slug string exists.

        :param host_slug: Host slug string
        :return: True or False, based on whether the host slug string
            exists
        """
        try:
            slug = host_slug.strip()
            if not slug:
                return False
        except ValueError:
            return False

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT hostslug FROM ww_hosts "
                 "WHERE hostslug = %s "
                 "LIMIT 1;")
        cursor.execute(query, (slug, ))
        result = cursor.fetchone()
        cursor.close()

        return bool(result)
