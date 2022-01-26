#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation


class Stats:
    """
    time-series statistics object in use when describing a time-series

    Attributes
    ----------
    top : any
        element that occurs most frequently
    unique : int
        number of unique elements
    frequency : int
        number of occurrences of the top element
    first : :class:`~autoai_ts_libs.deps.tspy.time_series.Observation.Observation`
        the first observation
    last : :class:`~autoai_ts_libs.deps.tspy.time_series.Observation.Observation`
        the last observation
    count : int
        number of elements in the time-series
    min_inter_arrival_time : int
        min time between observations
    max_inter_arrival_time : int
        max time between observations
    mean_inter_arrival_time : float
        mean time between observations
    """
    def __init__(self, tsc, j_stats):
        self._tsc = tsc
        self._j_stats = j_stats

    @property
    def top(self):
        """
        Returns
        -------
        any
            element that occurs most frequently
        """
        return self._j_stats.top()

    @property
    def unique(self):
        """
        Returns
        -------
        int
            number of unique elements
        """
        return self._j_stats.unique()

    @property
    def frequency(self):
        """
        Returns
        -------
        int
            number of occurrences of the top element
        """
        return self._j_stats.frequency()

    @property
    def first(self):
        """
        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.Observation.Observation`
            the first observation
        """
        j_first = self._j_stats.first()
        return Observation(self._tsc, j_first.getTimeTick(), j_first.getValue())

    @property
    def last(self):
        """
        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.Observation.Observation`
            the last observation
        """
        j_last = self._j_stats.last()
        return Observation(self._tsc, j_last.getTimeTick(), j_last.getValue())

    @property
    def count(self):
        """
        Returns
        -------
        int
            number of elements in the time-series
        """
        return self._j_stats.count()

    @property
    def min_inter_arrival_time(self):
        """
        Returns
        -------
        int
            min time between observations
        """
        return self._j_stats.minInterArrivalTime()

    @property
    def max_inter_arrival_time(self):
        """
        Returns
        -------
        int
            max time between observations
        """
        return self._j_stats.maxInterArrivalTime()

    @property
    def mean_inter_arrival_time(self):
        """
        Returns
        -------
        float
            mean time between observations
        """
        return self._j_stats.meanInterArrivalTime()

    def __str__(self):
        return self._j_stats.toString()

    def toString(self):
        return self._j_stats.toString()
