# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Panelist Scores Retrieval Functions
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from mysql.connector import connect
from wwdtm.panelist.utility import PanelistUtility
from wwdtm.validation import valid_int_id


class PanelistScores:
    """This class contains functions used to retrieve panelist scores
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

        self.utility = PanelistUtility(database_connection=self.database_connection)

    @lru_cache(typed=True)
    def retrieve_scores_by_id(self, panelist_id: int) -> List[int]:
        """Returns a list of panelist scores for appearances for the
        requested panelist ID.

        :param panelist_id: Panelist ID
        :return: List containing panelist scores. If panelist scores
            could not be retrieved, an empty list is returned.
        """
        if not valid_int_id(panelist_id):
            return []

        scores = []
        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT pm.panelistscore AS score "
                 "FROM ww_showpnlmap pm "
                 "JOIN ww_shows s ON s.showid = pm.showid "
                 "WHERE panelistid = %s "
                 "AND s.bestof = 0 and s.repeatshowid IS NULL "
                 "ORDER BY s.showdate ASC;")
        cursor.execute(query, (panelist_id, ))
        result = cursor.fetchall()
        cursor.close()

        if not result:
            return []

        for appearance in result:
            if appearance.score:
                scores.append(appearance.score)

        return scores

    @lru_cache(typed=True)
    def retrieve_scores_by_slug(self, panelist_slug: str
                                ) -> List[int]:
        """Returns a list of panelist scores for appearances for the
        requested panelist slug string.

        :param panelist_slug: Panelist slug string
        :return: List containing panelist scores. If panelist scores
            could not be retrieved, an empty list is returned.
        """
        id_ = self.utility.convert_slug_to_id(panelist_slug)
        if not id_:
            return []

        return self.retrieve_scores_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_scores_grouped_list_by_id(self, panelist_id: int
                                           ) -> Dict[str, List[int]]:
        """Returns a panelist's score grouping for the requested
        panelist ID.

        :param panelist_id: Panelist ID
        :return: Dictionary containing two lists, one containing scores
            and one containing counts of those scores. If panelist
            scores could not be retrieved, an empty dictionary is
            returned.
        """
        if not valid_int_id(panelist_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT MIN(pm.panelistscore) AS min, "
                 "MAX(pm.panelistscore) AS max "
                 "FROM ww_showpnlmap pm "
                 "LIMIT 1;")
        cursor.execute(query)
        result = cursor.fetchone()

        if not result:
            return {}

        min_score = result.min
        max_score = result.max

        scores = {}
        for score in range(min_score, max_score + 1):
            scores[score] = 0

        query = ("SELECT pm.panelistscore AS score, "
                 "COUNT(pm.panelistscore) AS score_count "
                 "FROM ww_showpnlmap pm "
                 "JOIN ww_shows s ON s.showid = pm.showid "
                 "WHERE pm.panelistid = %s "
                 "AND s.bestof = 0 AND s.repeatshowid IS NULL "
                 "AND pm.panelistscore IS NOT NULL "
                 "GROUP BY pm.panelistscore "
                 "ORDER BY pm.panelistscore ASC;")
        cursor.execute(query, (panelist_id, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return {}

        for row in results:
            scores[row.score] = row.score_count

        return {
            "score": list(scores.keys()),
            "count": list(scores.values()),
        }

    @lru_cache(typed=True)
    def retrieve_scores_grouped_list_by_slug(self, panelist_slug: str
                                             ) -> Dict[str, List[int]]:
        """Returns a panelist's score grouping for the requested
        panelist slug string.

        :param panelist_slug: Panelist slug string
        :return: Dictionary containing two lists, one containing scores
            and one containing counts of those scores. If panelist
            scores could not be retrieved, an empty dictionary is
            returned.
        """
        id_ = self.utility.convert_slug_to_id(panelist_slug)
        if not id_:
            return {}

        return self.retrieve_scores_grouped_list_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_scores_grouped_ordered_pair_by_id(self, panelist_id: int
                                                   ) -> List[Tuple[int, int]]:
        """Returns a list of tuples containing a score and the
        corresponding number of instances a panelist has scored that amount
        for the requested panelist ID.

        :param panelist_id: Panelist ID
        :return: List of tuples containing scores and score counts. If
            panelist scores could not be retrieved, an empty list is
            returned.
        """
        if not valid_int_id(panelist_id):
            return []

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT MIN(pm.panelistscore) AS min, "
                 "MAX(pm.panelistscore) AS max "
                 "FROM ww_showpnlmap pm;")
        cursor.execute(query)
        result = cursor.fetchone()

        if not result:
            return []

        min_score = result.min
        max_score = result.max

        scores = {}
        for score in range(min_score, max_score + 1):
            scores[score] = 0

        query = ("SELECT pm.panelistscore AS score, "
                 "COUNT(pm.panelistscore) AS score_count "
                 "FROM ww_showpnlmap pm "
                 "JOIN ww_shows s ON s.showid = pm.showid "
                 "WHERE pm.panelistid = %s "
                 "AND s.bestof = 0 AND s.repeatshowid IS NULL "
                 "AND pm.panelistscore IS NOT NULL "
                 "GROUP BY pm.panelistscore "
                 "ORDER BY pm.panelistscore ASC;")
        cursor.execute(query, (panelist_id, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        for row in results:
            scores[row.score] = row.score_count

        return list(scores.items())

    @lru_cache(typed=True)
    def retrieve_scores_grouped_ordered_pair_by_slug(self, panelist_slug: str,
                                                     ) -> List[Tuple[int, int]]:
        """Returns a list of tuples containing a score and the
        corresponding number of instances a panelist has scored that amount
        for the requested panelist slug string.

        :param panelist_slug: Panelist slug string
        :return: List of tuples containing scores and score counts. If
            panelist scores could not be retrieved, an empty list is
            returned.
        """
        id_ = self.utility.convert_slug_to_id(panelist_slug)
        if not id_:
            return []

        return self.retrieve_scores_grouped_ordered_pair_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_scores_list_by_id(self, panelist_id: int,
                                   ) -> Dict[str, List]:
        """Returns a dictionary containing two lists, one with show
        dates and one with corresponding scores for the requested
        panelist ID.

        :param panelist_id: Panelist ID
        :return: Dictionary containing a list show dates and a list
            of scores. If panelist scores could not be retrieved, an
            empty dictionary is returned.
        """
        if not valid_int_id(panelist_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT s.showdate AS date, pm.panelistscore AS score "
                 "FROM ww_showpnlmap pm "
                 "JOIN ww_shows s ON s.showid = pm.showid "
                 "WHERE pm.panelistid = %s "
                 "AND s.bestof = 0 AND s.repeatshowid IS NULL "
                 "AND pm.panelistscore IS NOT NULL "
                 "ORDER BY s.showdate ASC;")
        cursor.execute(query, (panelist_id, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return {}

        show_list = []
        score_list = []
        for shows in results:
            show_list.append(shows.date.isoformat())
            score_list.append(shows.score)

        return {
            "shows": show_list,
            "scores": score_list,
        }

    @lru_cache(typed=True)
    def retrieve_scores_list_by_slug(self, panelist_slug: str,
                                     ) -> Dict[str, List]:
        """Returns a dictionary containing two lists, one with show
        dates and one with corresponding scores for the requested
        panelist slug string.

        :param panelist_slug: Panelist slug string
        :return: Dictionary containing a list show dates and a list
            of scores. If panelist scores could not be retrieved, an
            empty dictionary is returned.
        """
        id_ = self.utility.convert_slug_to_id(panelist_slug)
        if not id_:
            return {}

        return self.retrieve_scores_list_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_scores_ordered_pair_by_id(self, panelist_id: int
                                           ) -> List[Tuple[str, int]]:
        """Returns a list of tuples containing a show date and the
        corresponding score for the requested panelist ID.

        :param panelist_id: Panelist ID
        :return: List of tuples containing show dates and scores. If
            panelist scores could not be retrieved, an empty list is
            returned.
        """
        if not valid_int_id(panelist_id):
            return []

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT s.showdate AS date, pm.panelistscore AS score "
                 "FROM ww_showpnlmap pm "
                 "JOIN ww_shows s ON s.showid = pm.showid "
                 "WHERE pm.panelistid = %s "
                 "AND s.bestof = 0 AND s.repeatshowid IS NULL "
                 "AND pm.panelistscore IS NOT NULL "
                 "ORDER BY s.showdate ASC;")
        cursor.execute(query, (panelist_id, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        scores = []
        for show in results:
            show_date = show.date.isoformat()
            score = show.score
            scores.append((show_date, score))

        return scores

    @lru_cache(typed=True)
    def retrieve_scores_ordered_pair_by_slug(self, panelist_slug: str,
                                             ) -> List[Tuple[str, int]]:
        """Returns a list of tuples containing a show date and the
        corresponding score for the requested panelist slug string.

        :param panelist_slug: Panelist slug string
        :return: List of tuples containing show dates and scores. If
            panelist scores could not be retrieved, an empty list is
            returned.
        """
        id_ = self.utility.convert_slug_to_id(panelist_slug)
        if not id_:
            return []

        return self.retrieve_scores_ordered_pair_by_id(id_)
