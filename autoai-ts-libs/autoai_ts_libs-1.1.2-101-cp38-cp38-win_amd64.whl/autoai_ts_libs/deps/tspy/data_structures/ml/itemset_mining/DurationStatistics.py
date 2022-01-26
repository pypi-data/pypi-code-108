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

class DurationStatistics:
    """
    This is a deeper statistics holder class that maintains the duration statistics, where duration statistics is the
    duration of a given match in a time-series. The duration will be taken of each match, and a set of aggregates will
    be computed based on the all of the occurrences of that match.

    Attributes
    ----------
    min : int
        minimum duration
    max : int
        maximum duration
    sum : int
        sum of all durations
    count : int
        total count of matches
    average : float
        average duration
    sd : float
        standard deviation of durations
    min_lead_time : int
        minimum lead time to match
    max_lead_time : int
        maximum lead time to match
    sum_lead_time : int
        sum of lead time to match
    average_lead_time : float
        average of lead time to match
    sd_lead_time : float
        standard deviation of lead time to match
    min_end_time : int
        minimum end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
    max_end_time : int
        maximum end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
    sum_end_time : int
        sum end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
    average_end_time : float
        average end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
    sd_end_time : float
        standard deviation of end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
    variance : float
        variance of duration
    variance_lead_time : float
        variance of lead time to match
    variance_end_time : float
        variance of end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
    """

    def __init__(self, j_duration_statistics):
        self._j_duration_statistics = j_duration_statistics

    @property
    def min(self):
        """
        Returns
        -------
        int
            minimum duration
        """
        return self._j_duration_statistics.min()

    @property
    def max(self):
        """
        Returns
        -------
        int
            maximum duration
        """
        return self._j_duration_statistics.max()

    @property
    def sum(self):
        """
        Returns
        -------
        int
            sum of all durations
        """
        return self._j_duration_statistics.sum()

    @property
    def count(self):
        """
        Returns
        -------
        int
            total count of matches
        """
        return self._j_duration_statistics.count()

    @property
    def average(self):
        """
        Returns
        -------
        float
            average duration
        """
        return self._j_duration_statistics.average()

    @property
    def sd(self):
        """
        Returns
        -------
        float
            standard deviation of durations
        """
        return self._j_duration_statistics.sd()

    @property
    def min_lead_time(self):
        """
        Returns
        -------
        int
            minimum lead time to match
        """
        return self._j_duration_statistics.minLeadTime()

    @property
    def max_lead_time(self):
        """
        Returns
        -------
        int
            maximum lead time to match
        """
        return self._j_duration_statistics.maxLeadTime()

    @property
    def sum_lead_time(self):
        """
        Returns
        -------
        int
            sum of lead time to match
        """
        return self._j_duration_statistics.sumLeadTime()

    @property
    def average_lead_time(self):
        """
        Returns
        -------
        float
            average of lead time to match
        """
        return self._j_duration_statistics.averageLeadTime()

    @property
    def sd_lead_time(self):
        """
        Returns
        -------
        float
            standard deviation of lead time to match
        """
        return self._j_duration_statistics.sdLeadTime()

    @property
    def min_end_time(self):
        """
        Returns
        -------
        int
            minimum end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
        """
        return self._j_duration_statistics.minEndTime()

    @property
    def max_end_time(self):
        """
        Returns
        -------
        int
            maximum end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
        """
        return self._j_duration_statistics.maxEndTime()

    @property
    def sum_end_time(self):
        """
        Returns
        -------
        int
            sum of end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
        """
        return self._j_duration_statistics.sumEndTime()

    @property
    def average_end_time(self):
        """
        Returns
        -------
        int
            average of end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
        """
        return self._j_duration_statistics.averageEndTime()

    @property
    def sd_end_time(self):
        """
        Returns
        -------
        int
            standard deviation of end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
        """
        return self._j_duration_statistics.sdEndTime()

    @property
    def variance(self):
        """
        Returns
        -------
        float
            variance of duration
        """
        return self._j_duration_statistics.variance()

    @property
    def variance_lead_time(self):
        """
        Returns
        -------
        float
            variance of lead time to match
        """
        return self._j_duration_statistics.varianceLeadTime()

    @property
    def variance_end_time(self):
        """
        Returns
        -------
        float
            variance of end time to match. End time is defined as the difference of the series last time-tick and the matches
        last time-tick
        """
        return self._j_duration_statistics.varianceEndTime()

    def __str__(self):
        return self._j_duration_statistics.toString()
