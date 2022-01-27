# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Scorekeeper Data Retrieval Functions
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional

from mysql.connector import connect
from slugify import slugify
from wwdtm.scorekeeper.appearances import ScorekeeperAppearances
from wwdtm.scorekeeper.utility import ScorekeeperUtility
from wwdtm.validation import valid_int_id


class Scorekeeper:
    """This class contains functions used to retrieve scorekeeper data
    from a copy of the Wait Wait Stats database.

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

        self.appearances = ScorekeeperAppearances(database_connection=self.database_connection)
        self.utility = ScorekeeperUtility(database_connection=self.database_connection)

    def retrieve_all(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing scorekeeper
        ID, name and slug string for all scorekeepers.

        :return: List of all scorekeepers and their corresponding
            information. If scorekeeper information could not be
            retrieved, an empty list will be returned.
        """
        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT scorekeeperid AS id, scorekeeper AS name, "
                 "scorekeeperslug AS slug, scorekeepergender AS gender "
                 "FROM ww_scorekeepers "
                 "ORDER BY scorekeeper ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        scorekeepers = []
        for row in results:
            scorekeepers.append({
                "id": row.id,
                "name": row.name,
                "gender": row.gender,
                "slug": row.slug if row.slug else slugify(row.name),
            })

        return scorekeepers

    def retrieve_all_details(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing scorekeeper
        ID, name, slug string and appearance information for all
        scorekeepers.

        :return: List of all scorekeepers and their corresponding
            information and appearances. If scorekeeper information
            could not be retrieved, an empty list will be returned.
        """
        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT scorekeeperid AS id, scorekeeper AS name, "
                 "scorekeeperslug AS slug, scorekeepergender AS gender "
                 "FROM ww_scorekeepers "
                 "ORDER BY scorekeeper ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        scorekeepers = []
        for row in results:
            scorekeepers.append({
                "id": row.id,
                "name": row.name,
                "slug": row.slug if row.slug else slugify(row.name),
                "gender": row.gender,
                "appearances": self.appearances.retrieve_appearances_by_id(row.id)
            })

        return scorekeepers

    def retrieve_all_ids(self) -> List[int]:
        """Returns a list of all scorekeeper IDs from the database,
        sorted by scorekeeper name.

        :return: List of all scorekeeper IDs. If scorekeeper IDs could
            not be retrieved, an empty list would be returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT scorekeeperid FROM ww_scorekeepers "
                 "ORDER BY scorekeeper ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [v[0] for v in results]

    def retrieve_all_slugs(self) -> List[str]:
        """Returns a list of all scorekeeper slug strings from the
        database, sorted by scorekeeper name.

        :return: List of all scorekeeper slug strings. If scorekeeper
            slug strings could not be retrieved, an empty list will be
            returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT scorekeeperslug FROM ww_scorekeepers "
                 "ORDER BY scorekeeper ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [v[0] for v in results]

    @lru_cache(typed=True)
    def retrieve_by_id(self, scorekeeper_id: int) -> Dict[str, Any]:
        """Returns a dictionary object containing scorekeeper ID, name
        and slug string for the requested scorekeeper ID.

        :param scorekeeper_id: Scorekeeper ID
        :return: Dictionary containing scorekeeper information. If
            scorekeeper information could not be retrieved, an empty
            dictionary will be returned.
        """
        if not valid_int_id(scorekeeper_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT scorekeeperid AS id, scorekeeper AS name, "
                 "scorekeeperslug AS slug, scorekeepergender AS gender "
                 "FROM ww_scorekeepers "
                 "WHERE scorekeeperid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (scorekeeper_id, ))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return {}

        return {
            "id": result.id,
            "name": result.name,
            "slug": result.slug if result.slug else slugify(result.name),
            "gender": result.gender,
        }

    @lru_cache(typed=True)
    def retrieve_by_slug(self, scorekeeper_slug: str) -> Dict[str, Any]:
        """Returns a dictionary object containing scorekeeper ID, name
        and slug string for the requested scorekeeper slug string.

        :param scorekeeper_slug: Scorekeeper slug string
        :return: Dictionary containing scorekeeper information. If
            scorekeeper information could not be retrieved, an empty
            dictionary will be returned.
        """
        try:
            slug = scorekeeper_slug.strip()
            if not slug:
                return {}
        except AttributeError:
            return {}

        id_ = self.utility.convert_slug_to_id(slug)
        if not id_:
            return {}

        return self.retrieve_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_details_by_id(self, scorekeeper_id: int) -> Dict[str, Any]:
        """Returns a dictionary object containing scorekeeper ID, name,
        slug string and appearance information for the requested
        scorekeeper ID.

        :param scorekeeper_id: Scorekeeper ID
        :return: Dictionary containing scorekeeper information and
            their appearances. If scorekeeper information could not be
            retrieved, an empty dictionary will be returned.
        """
        if not valid_int_id(scorekeeper_id):
            return {}

        info = self.retrieve_by_id(scorekeeper_id)
        if not info:
            return {}

        info["appearances"] = self.appearances.retrieve_appearances_by_id(scorekeeper_id)

        return info

    @lru_cache(typed=True)
    def retrieve_details_by_slug(self, scorekeeper_slug: str) -> Dict[str, Any]:
        """Returns a dictionary object containing scorekeeper ID, name,
        slug string and appearance information for the requested
        scorekeeper slug string.

        :param scorekeeper_slug: Scorekeeper slug string
        :return: Dictionary containing scorekeeper information and
            their appearances. If scorekeeper information could not be
            retrieved, an empty dictionary will be returned.
        """
        try:
            slug = scorekeeper_slug.strip()
            if not slug:
                return {}
        except AttributeError:
            return {}

        id_ = self.utility.convert_slug_to_id(slug)
        if not id_:
            return {}

        return self.retrieve_details_by_id(id_)
