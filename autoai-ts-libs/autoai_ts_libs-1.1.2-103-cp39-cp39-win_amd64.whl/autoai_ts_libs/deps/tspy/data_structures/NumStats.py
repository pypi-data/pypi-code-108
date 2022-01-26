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

from autoai_ts_libs.deps.tspy.data_structures.Stats import Stats


class NumStats(Stats):
    """
    numeric time-series statistics object in use when describing a time-series

    Attributes
    ----------
    mean : float
        mean of all values in the time-series
    std : float
        std of all values in the time-series
    min : float
        min value in the time-series
    max : float
        max value in the time-series
    _25 : float
        25th percentile in the time-series
    _50 : float
        50th percentile in the time-series
    _75 : float
        75th percentile in the time-series
    """
    def __init__(self, tsc, j_num_stats):
        super().__init__(tsc, j_num_stats)
        self._tsc = tsc
        self._j_num_stats = j_num_stats

    @property
    def mean(self):
        """
        Returns
        -------
        float
            mean of all values in the time-series
        """
        return self._j_num_stats.mean()

    @property
    def std(self):
        """
        Returns
        -------
        float
            std of all values in the time-series
        """
        return self._j_num_stats.std()

    @property
    def min(self):
        """
        Returns
        -------
        float
            min value in the time-series
        """
        return self._j_num_stats.min()

    @property
    def max(self):
        """
        Returns
        -------
        float
            max value in the time-series
        """
        return self._j_num_stats.max()

    @property
    def _25(self):
        """
        Returns
        -------
        float
            25th percentile in the time-series
        """
        return self._j_num_stats._25()

    @property
    def _50(self):
        """
        Returns
        -------
        float
            50th percentile in the time-series
        """
        return self._j_num_stats._50()

    @property
    def _75(self):
        """
        Returns
        -------
        float
            75th percentile in the time-series
        """
        return self._j_num_stats._75()

    def __str__(self):
        return self._j_num_stats.toString()

    def toString(self):
        return self._j_num_stats.toString()

