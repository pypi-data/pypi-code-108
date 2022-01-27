# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Guest Data Retrieval Functions
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional

from mysql.connector import connect
from slugify import slugify
from wwdtm.guest.appearances import GuestAppearances
from wwdtm.guest.utility import GuestUtility
from wwdtm.validation import valid_int_id


class Guest:
    """This class contains functions used to retrieve guest data from a
    copy of the Wait Wait Stats database.

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

        self.appearances = GuestAppearances(database_connection=self.database_connection)
        self.utility = GuestUtility(database_connection=self.database_connection)

    def retrieve_all(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing guest ID,
        name and slug string for all guests.

        :return: List of all guests and their corresponding
            information. If guests could not be retrieved, an empty list
            is returned.
        """

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT guestid AS id, guest AS name, guestslug AS slug "
                 "FROM ww_guests "
                 "WHERE guestslug != 'none' "
                 "ORDER BY guest ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        guests = []
        for row in results:
            guests.append({
                "id": row.id,
                "name": row.name,
                "slug": row.slug if row.slug else slugify(row.name),
            })

        return guests

    def retrieve_all_details(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing guest ID,
        name, slug string and appearance information for all guests.

        :return: List of all guests and their corresponding
            information and appearances. If guests could not be
            retrieved, an empty list is returned.
        """
        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT guestid AS id, guest AS name, guestslug AS slug "
                 "FROM ww_guests "
                 "WHERE guestslug != 'none' "
                 "ORDER BY guest ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        guests = []
        for row in results:
            guests.append({
                "id": row.id,
                "name": row.name,
                "slug": row.slug if row.slug else slugify(row.name),
                "appearances": self.appearances.retrieve_appearances_by_id(row.id),
            })

        return guests

    def retrieve_all_ids(self) -> List[int]:
        """Returns a list of all guest IDs from the database, sorted by
        guest name.

        :return: List of all guest IDs. If guest IDs could not be
            retrieved, an emtpy list is returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT guestid FROM ww_guests "
                 "WHERE guestslug != 'none' "
                 "ORDER BY guest ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [v[0] for v in results]

    def retrieve_all_slugs(self) -> List[str]:
        """Returns a list of all guest slug strings from the database,
        sorted by guest name.

        :return: List of all guest slug strings. If guest slug strings
            could not be retrieved, an emtpy list is returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT guestslug FROM ww_guests "
                 "WHERE guestslug != 'none' "
                 "ORDER BY guest ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [v[0] for v in results]

    @lru_cache(typed=True)
    def retrieve_by_id(self, guest_id: int) -> Dict[str, Any]:
        """Returns a dictionary object containing guest ID, name and
        slug string for the requested guest ID.

        :param guest_id: Guest ID
        :return: Dictionary containing guest information. If guest
            information could not be retrieved, an empty dictionary is
            returned.
        """
        if not valid_int_id(guest_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT guestid AS id, guest AS name, guestslug AS slug "
                 "FROM ww_guests "
                 "WHERE guestid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (guest_id, ))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return {}

        return {
            "id": result.id,
            "name": result.name,
            "slug": result.slug if result.slug else slugify(result.name),
        }

    @lru_cache(typed=True)
    def retrieve_by_slug(self, guest_slug: str) -> Dict[str, Any]:
        """Returns a dictionary object containing guest ID, name and
        slug string for the requested guest slug string.

        :param guest_slug: Guest slug string
        :return: Dictionary containing guest information. If guest
            information could not be retrieved, an empty dictionary is
            returned.
        """
        try:
            slug = guest_slug.strip()
            if not slug:
                return {}
        except AttributeError:
            return {}

        id_ = self.utility.convert_slug_to_id(slug)
        if not id_:
            return {}

        return self.retrieve_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_details_by_id(self, guest_id: int) -> Dict[str, Any]:
        """Returns a dictionary object containing guest ID, name, slug
        string and appearance information for the requested Guest ID.

        :param guest_id: Guest ID
        :return: Dictionary containing guest information and their
            appearances. If guest information could not be retrieved,
            an empty dictionary is returned.
        """
        if not valid_int_id(guest_id):
            return {}

        info = self.retrieve_by_id(guest_id)
        if not info:
            return {}

        info["appearances"] = self.appearances.retrieve_appearances_by_id(guest_id)

        return info

    @lru_cache(typed=True)
    def retrieve_details_by_slug(self, guest_slug: str) -> Dict[str, Any]:
        """Returns a dictionary object containing guest ID, name, slug
        string and appearance information for the requested Guest slug
        string.

        :param guest_slug: Guest slug string
        :return: Dictionary containing guest information and their
            appearances. If guest information could not be retrieved,
            an empty dictionary is returned.
        """
        try:
            slug = guest_slug.strip()
            if not slug:
                return {}
        except AttributeError:
            return {}

        id_ = self.utility.convert_slug_to_id(slug)
        if not id_:
            return {}

        return self.retrieve_details_by_id(id_)
