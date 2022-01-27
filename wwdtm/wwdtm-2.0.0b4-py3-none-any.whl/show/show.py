# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
"""Wait Wait Don't Tell Me! Stats Show Data Retrieval Functions
"""
import datetime
import dateutil.parser as date_parser
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from mysql.connector import connect
from wwdtm.show.info import ShowInfo
from wwdtm.show.info_multiple import ShowInfoMultiple
from wwdtm.show.utility import ShowUtility
from wwdtm.validation import valid_int_id


class Show:
    """This class contains functions used to retrieve show data from a
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

        self.info = ShowInfo(database_connection=self.database_connection)
        self.info_multiple = ShowInfoMultiple(database_connection=self.database_connection)
        self.utility = ShowUtility(database_connection=self.database_connection)

    def retrieve_all(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing show ID,
        show date, Best Of and Repeat Show information for all shows.

        :return: List of all shows and their corresponding information.
            If show information could not be retrieved, an empty list
            will be returned.
        """
        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT showid AS id, showdate AS date, "
                 "bestof AS best_of, repeatshowid AS repeat_show_id "
                 "FROM ww_shows "
                 "ORDER BY showdate ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        shows = []
        for row in results:
            show = {
                "id": row.id,
                "date": row.date.isoformat(),
                "best_of": bool(row.best_of),
                "repeat_show": bool(row.repeat_show_id),
            }

            if row.repeat_show_id:
                show["original_show_id"] = row.repeat_show_id
                show["original_show_date"] = self.utility.convert_id_to_date(row.repeat_show_id)

            shows.append(show)

        return shows

    def retrieve_all_details(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing show ID,
        show date, host, scorekeeper, panelist and guest information
        for all shows.

        :return: List of all shows and their corresponding details.
            If show information could not be retrieved, an empty list
            will be returned.
        """
        info = self.info_multiple.retrieve_core_info_all()

        if not info:
            return []

        panelists = self.info_multiple.retrieve_panelist_info_all()
        bluffs = self.info_multiple.retrieve_bluff_info_all()
        guests = self.info_multiple.retrieve_guest_info_all()

        shows = []
        for show in info:
            if info[show]["id"] in panelists:
                info[show]["panelists"] = panelists[info[show]["id"]]
            else:
                info[show]["panelists"] = []

            if info[show]["id"] in bluffs:
                info[show]["bluff"] = bluffs[info[show]["id"]]
            else:
                info[show]["bluff"] = []

            if info[show]["id"] in guests:
                info[show]["guests"] = guests[info[show]["id"]]
            else:
                info[show]["guests"] = []

            shows.append(info[show])

        return shows

    def retrieve_all_ids(self) -> List[int]:
        """Returns a list of all show IDs from the database, sorted by
        show date.

        :return: List of all show IDs. If show IDs could not be
            retrieved, an empty list will be returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "ORDER BY showdate ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [v[0] for v in results]

    def retrieve_all_dates(self) -> List[str]:
        """Returns a list of all show dates from the database, sorted
        by show date.

        :return: List of all show date strings. If show dates could not
            be retrieved, an empty list will be returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showdate FROM ww_shows "
                 "ORDER BY showdate ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [v[0].isoformat() for v in results]

    def retrieve_all_dates_tuple(self) -> List[Tuple[int, int, int]]:
        """Returns a list of all show dates as a tuple of year, month,
        and day, sorted by show date.

        :return: List of allow show dates as a tuple of year, month
            and day. If show dates could not be retrieved, an empty list
            will be returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT YEAR(showdate), MONTH(showdate), DAY(showdate) "
                 "FROM ww_shows "
                 "ORDER BY showdate ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [tuple(v) for v in results]

    def retrieve_all_show_years_months(self) -> List[str]:
        """Returns a list of all show years and months as a string,
        sorted by year and month.

        :return: List of all show years and month in ``YYYY-MM`` format.
            If show dates could not be retrieved, an empty list will be
            returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT DISTINCT YEAR(showdate), MONTH(showdate) "
                 "FROM ww_shows "
                 "ORDER BY showdate ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [f"{v[0]}-{v[1]}" for v in results]

    def retrieve_all_shows_years_months_tuple(self) -> List[Tuple[int, int]]:
        """Returns a list of all show years and months as a tuple of
        year and month, sorted by year and month.

        :return: List of allow show dates as a tuple of year and month.
            If show dates could not be retrieved, an empty list will be
            returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT DISTINCT YEAR(showdate), MONTH(showdate) "
                 "FROM ww_shows "
                 "ORDER BY showdate ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [tuple(v) for v in results]

    @lru_cache(typed=True)
    def retrieve_by_date(self,
                         year: int,
                         month: int,
                         day: int) -> Dict[str, Any]:
        """Returns a dictionary object containing show ID, show date,
        Best Of and Repeat Show information for the requested show date.

        :param year: Four-digit year
        :param month: One or two-digit month
        :param day: One or two-digit day
        :return: Dictionary containing show information. If show
            information could not be retrieved, an empty dictionary will
            be returned.
        """
        id_ = self.utility.convert_date_to_id(year, month, day)
        if not id_:
            return {}

        return self.retrieve_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_by_date_string(self,
                                date_string: str) -> Dict[str, Any]:
        """Returns a dictionary object containing show ID, show date,
        Best Of and Repeat Show information for the requested show date
        string.

        :param date_string: Show date in ``YYYY-MM-DD`` format
        :return: Dictionary containing show information. If show
            information could not be retrieved, an empty dictionary will
            be returned.
        """
        try:
            parsed_date_string = date_parser.parse(date_string)
        except ValueError:
            return {}

        id_ = self.utility.convert_date_to_id(parsed_date_string.year,
                                              parsed_date_string.month,
                                              parsed_date_string.day)

        return self.retrieve_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_by_id(self, show_id: int) -> Dict[str, Any]:
        """Returns a dictionary object containing show ID, show date,
        Best Of and Repeat Show information for the requested show ID.

        :param show_id: Show ID
        :return: Dictionary containing show information. If show
            information could not be retrieved, an empty dictionary will
            be returned.
        """
        if not valid_int_id(show_id):
            return {}

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT showid AS id, showdate AS date, "
                 "bestof AS best_of, repeatshowid AS repeat_show_id "
                 "FROM ww_shows "
                 "WHERE showid = %s "
                 "LIMIT 1;")
        cursor.execute(query, (show_id, ))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return {}

        info = {
            "id": result.id,
            "date": result.date.isoformat(),
            "best_of": bool(result.best_of),
            "repeat_show": bool(result.repeat_show_id),
        }

        if result.repeat_show_id:
            info["original_show_id"] = result.repeat_show_id
            info["original_show_date"] = self.utility.convert_id_to_date(result.repeat_show_id)

        return info

    @lru_cache(typed=True)
    def retrieve_by_month_day(self, month: int, day: int) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing with show
        information for the requested month and day, sorted by year.

        :param month: One or two-digit month
        :param day: One or two-digit day
        :return: List of shows for the requested month, day, and
            corresponding information. If show information could not be
            retrieved, an empty list will be returned.
        """
        if not 1 <= month <= 12 or not 1 <= day <= 31:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "WHERE MONTH(showdate) = %s "
                 "AND DAY(showdate) = %s "
                 "ORDER BY showdate ASC;")
        cursor.execute(query, (month, day, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [self.retrieve_by_id(v[0]) for v in results]

    @lru_cache(typed=True)
    def retrieve_by_year(self, year: int) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing with show
        information for the requested year, sorted by show date.

        :param year: Four-digit year
        :return: List of shows for the requested year and corresponding
            information. If show information could not be retrieved,
            an empty list will be returned.
        """
        try:
            parsed_year = date_parser.parse(f"{year:04d}")
        except ValueError:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "WHERE YEAR(showdate) = %s "
                 "ORDER BY showdate ASC;")
        cursor.execute(query, (parsed_year.year, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [self.retrieve_by_id(v[0]) for v in results]

    @lru_cache(typed=True)
    def retrieve_by_year_month(self,
                               year: int,
                               month: int) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing show
        information for the requested year and month, sorted by show
        date.

        :param year: Four-digit year
        :param month: One or two-digit month
        :return: List of shows for the requested year and month, and
            corresponding information. If show information could not be
            retrieved, a list of dictionaries will be returned.
        """
        try:
            parsed_year_month = date_parser.parse(f"{year:04d}-{month:02d}-01")
        except ValueError:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "WHERE YEAR(showdate) = %s "
                 "AND MONTH(showdate) = %s ORDER BY showdate ASC;")
        cursor.execute(query, (parsed_year_month.year,
                               parsed_year_month.month, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [self.retrieve_by_id(v[0]) for v in results]

    @lru_cache(typed=True)
    def retrieve_details_by_date(self,
                                 year: int,
                                 month: int,
                                 day: int) -> Dict[str, Any]:
        """Returns a list of dictionary objects containing show ID,
        show date, host, scorekeeper, panelist and guest information
        for the requested show date.

        :param year: Four-digit year
        :param month: One or two-digit month
        :param day: One or two digit day
        :return: Dictionary containing show information and details. If
            show information could not be retrieved, an empty dictionary
            will be returned.
        """
        id_ = self.utility.convert_date_to_id(year, month, day)
        if not id_:
            return {}

        return self.retrieve_details_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_details_by_date_string(self,
                                        date_string: str) -> Dict[str, Any]:
        """Returns a list of dictionary objects containing show ID,
        show date, host, scorekeeper, panelist and guest information
        for the requested show date string.

        :param date_string: Show date in ``YYYY-MM-DD`` format
        :return: Dictionary containing show information and details. If
            show information could not be retrieved, an empty dictionary
            will be returned.
        """
        try:
            parsed_date_string = date_parser.parse(date_string)
        except ValueError:
            return {}

        id_ = self.utility.convert_date_to_id(parsed_date_string.year,
                                              parsed_date_string.month,
                                              parsed_date_string.day)

        return self.retrieve_details_by_id(id_)

    @lru_cache(typed=True)
    def retrieve_details_by_id(self, show_id: int) -> Dict[str, Any]:
        """Returns a list of dictionary objects containing show ID,
        show date, host, scorekeeper, panelist and guest information
        for the requested show ID.

        :param show_id: Show ID
        :return: Dictionary containing show information and details. If
            show information could not be retrieved, an empty dictionary
            will be returned.
        """
        if not valid_int_id(show_id):
            return {}

        info = self.info.retrieve_core_info_by_id(show_id)
        if not info:
            return {}

        info["panelists"] = self.info.retrieve_panelist_info_by_id(show_id)
        info["bluff"] = self.info.retrieve_bluff_info_by_id(show_id)
        info["guests"] = self.info.retrieve_guest_info_by_id(show_id)

        return info

    @lru_cache(typed=True)
    def retrieve_details_by_month_day(self, month: int, day: int
                                      ) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing show ID,
        show date, host, scorekeeper, panelist and guest information
        for the requested month and day, sorted by year.

        :param month: One or two-digit month
        :param day: One or two-digit day
        :return: Dictionary containing show information and details. If
            show information could not be retrieved, an empty dictionary
            will be returned.
        """
        if not 1 <= month <= 12 or not 1 <= day <= 31:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "WHERE MONTH(showdate) = %s "
                 "AND DAY(showdate) = %s "
                 "ORDER BY showdate ASC;")
        cursor.execute(query, (month, day, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        show_ids = [v[0] for v in results]
        info = self.info_multiple.retrieve_core_info_by_ids(show_ids)

        if not info:
            return []

        shows = []
        for show in info:
            if info[show]:
                info[show]["panelists"] = self.info.retrieve_panelist_info_by_id(info[show]["id"])
                info[show]["bluff"] = self.info.retrieve_bluff_info_by_id(info[show]["id"])
                info[show]["guests"] = self.info.retrieve_guest_info_by_id(info[show]["id"])
                shows.append(info[show])

        return shows

    @lru_cache(typed=True)
    def retrieve_details_by_year(self, year: int) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing show ID,
        show date, host, scorekeeper, panelist and guest information for
        the requested year, sorted by show date.

        :param year: Four-digit year
        :return: List of shows for the requested year and corresponding
            details. If show information could not be retrieved, an
            empty list will be returned.
        """
        try:
            parsed_year = date_parser.parse(f"{year:04d}")
        except ValueError:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "WHERE YEAR(showdate) = %s "
                 "ORDER BY showdate ASC;")
        cursor.execute(query, (parsed_year.year, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        show_ids = [v[0] for v in results]
        info = self.info_multiple.retrieve_core_info_by_ids(show_ids)

        if not info:
            return []

        shows = []
        for show in info:
            if info[show]:
                info[show]["panelists"] = self.info.retrieve_panelist_info_by_id(info[show]["id"])
                info[show]["bluff"] = self.info.retrieve_bluff_info_by_id(info[show]["id"])
                info[show]["guests"] = self.info.retrieve_guest_info_by_id(info[show]["id"])
                shows.append(info[show])

        return shows

    @lru_cache(typed=True)
    def retrieve_details_by_year_month(self,
                                       year: int,
                                       month: int) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing show ID,
        show date, host, scorekeeper, panelist and guest information for
        the requested year and month, sorted by show date.

        :param year: Four-digit year
        :param month: One or two-digit month
        :return: List of shows for the requested year and month, and
            corresponding details. If show information could not be
            retrieved, an empty list will be returned.
        """
        try:
            parsed_year_month = date_parser.parse(f"{year:04d}-{month:02d}-01")
        except ValueError:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "WHERE YEAR(showdate) = %s "
                 "AND MONTH(showdate) = %s "
                 "ORDER BY showdate ASC;")
        cursor.execute(query, (parsed_year_month.year,
                               parsed_year_month.month, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        show_ids = [v[0] for v in results]
        info = self.info_multiple.retrieve_core_info_by_ids(show_ids)

        if not info:
            return []

        shows = []
        for show in info:
            if info[show]:
                info[show]["panelists"] = self.info.retrieve_panelist_info_by_id(info[show]["id"])
                info[show]["bluff"] = self.info.retrieve_bluff_info_by_id(info[show]["id"])
                info[show]["guests"] = self.info.retrieve_guest_info_by_id(info[show]["id"])
                shows.append(info[show])

        return shows

    @lru_cache(typed=True)
    def retrieve_months_by_year(self,
                                year: int) -> List[int]:
        """Returns a list of show months available for the requested
        year, sorted by month.

        :param year: Four-digit year
        :return: List of available show months. If show information
            could not be retrieved, an empty list will be returned.
        """
        try:
            _ = date_parser.parse(f"{year:04d}")
        except ValueError:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT DISTINCT MONTH(showdate) "
                 "FROM ww_shows "
                 "WHERE YEAR(showdate) = %s "
                 "ORDER BY MONTH(showdate) ASC;")
        cursor.execute(query, (year,))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [v[0] for v in results]

    @lru_cache(typed=True)
    def retrieve_recent(self,
                        include_days_ahead: Optional[int] = 7,
                        include_days_back: Optional[int] = 32
                        ) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing show ID,
        show date, Best Of and Repeat Show information for recent shows.

        :param include_days_ahead: Number of days in the future to
            include, defaults to 7
        :param include_days_back: Number of days in the past to
            include, defaults to 32
        :return: List of recent shows and corresponding information. If
            show information could not be retrieved, an empty list will
            be returned.
        """
        try:
            past_days = int(include_days_back)
            future_days = int(include_days_ahead)
        except ValueError:
            return []

        try:
            past_date = datetime.datetime.now() - datetime.timedelta(days=past_days)
            future_date = datetime.datetime.now() + datetime.timedelta(days=future_days)
        except OverflowError:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "WHERE showdate >= %s AND "
                 "showdate <= %s ORDER BY showdate ASC;")
        cursor.execute(query, (past_date.isoformat(),
                               future_date.isoformat(), ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [self.retrieve_by_id(v[0]) for v in results]

    @lru_cache(typed=True)
    def retrieve_recent_details(self,
                                include_days_ahead: Optional[int] = 7,
                                include_days_back: Optional[int] = 32
                                ) -> List[Dict[str, Any]]:
        """Returns a list of dictionary objects containing show ID,
        show date, host, scorekeeper, panelist and guest information
        for recent shows.

        :param include_days_ahead: Number of days in the future to
            include, defaults to 7
        :param include_days_back: Number of days in the past to
            include, defaults to 32
        :return: List of recent shows and corresponding details. If show
            information could not be retrieved, an empty list will be
            returned.
        """
        try:
            past_days = int(include_days_back)
            future_days = int(include_days_ahead)
        except ValueError:
            return []

        try:
            past_date = datetime.datetime.now() - datetime.timedelta(days=past_days)
            future_date = datetime.datetime.now() + datetime.timedelta(days=future_days)
        except OverflowError:
            return []

        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT showid FROM ww_shows "
                 "WHERE showdate >= %s AND "
                 "showdate <= %s ORDER BY showdate ASC;")
        cursor.execute(query, (past_date.isoformat(),
                               future_date.isoformat(), ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        show_ids = [v[0] for v in results]
        info = self.info_multiple.retrieve_core_info_by_ids(show_ids)

        if not info:
            return []

        shows = []
        for show in info:
            info[show]["panelists"] = self.info.retrieve_panelist_info_by_id(show)
            info[show]["bluff"] = self.info.retrieve_bluff_info_by_id(show)
            info[show]["guests"] = self.info.retrieve_guest_info_by_id(show)
            shows.append(info[show])

        return shows

    @lru_cache(typed=True)
    def retrieve_scores_by_year(self, year: int) -> List[Tuple]:
        """Returns a list of tuples containing panelist scores for all
        shows in the requested year, sorted by show date.

        :param year: Four-digit year
        :return: List of tuples each containing show date and panelist
            scores. If show scores could not be retrieved, an empty list
            will be returned.
        """
        try:
            _ = date_parser.parse(f"{year:04d}")
        except ValueError:
            return []

        cursor = self.database_connection.cursor(named_tuple=True)
        query = ("SELECT s.showdate AS date, pm.panelistscore AS score "
                 "FROM ww_showpnlmap pm "
                 "JOIN ww_shows s ON s.showid = pm.showid "
                 "WHERE s.bestof = 0 AND s.repeatshowid IS NULL "
                 "AND pm.panelistscore IS NOT NULL "
                 "AND YEAR(s.showdate) = %s "
                 "ORDER BY s.showdate ASC, pm.panelistscore ASC;")
        cursor.execute(query, (year, ))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        shows = {}
        for row in results:
            date = row.date.isoformat()
            if date not in shows:
                shows[date] = []

            shows[date].append(row.score)

        show_scores = []
        for show in shows:
            show_score = shows[show]
            show_score.insert(0, show)
            show_scores.append(tuple(show_score))

        return show_scores

    def retrieve_years(self) -> List[int]:
        """Returns a list of available show years, sorted by year.

        :return: List of available show years. If show dates could not
            be retrieved, an empty list will be returned.
        """
        cursor = self.database_connection.cursor(dictionary=False)
        query = ("SELECT DISTINCT YEAR(showdate) "
                 "FROM ww_shows "
                 "ORDER BY YEAR(showdate) ASC;")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if not results:
            return []

        return [v[0] for v in results]
