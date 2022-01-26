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

from autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DurationStatistics import DurationStatistics


class FrequentItemSetStatistics:
    """
    container class representing Frequent-Itemset Statistics

    This class provides various statistics on the item-set, this is associated with the Frequent ItemSet Mining
    Algorithm. Statistics range from (1) Coverage, (2) Duration statistics

    Attributes
    ----------
    original_size : int
        indicating the number of sequences that match the itemset
    duration_statistics : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DurationStatistics.DurationStatistics`
        statistics related to duration of match in time-series
    binary_match_normalized_frequency : int
        indicating number of matches in the set, where any number of matches for a given itemset counts as a single
        match
    multi_match_norm_frequency : int
        provides the total number of matches given a set of sets and a subset, with one
        set possibly matching a subset multiple times.
    coverage : float
        The coverage (binary_match_normalized_frequency / original_size) of the set for the FIM itemset
    """

    def __init__(self, j_statistics):
        self._j_statistics = j_statistics
        self._duration_statistics = DurationStatistics(j_statistics.durationStatistics())

    @property
    def original_size(self):
        """
        Returns
        -------
        int
            the number of sequences that match the itemset
        """
        return self._j_statistics.originalSize()

    @property
    def duration_statistics(self):
        """
        Returns
        -------
        :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DurationStatistics.DurationStatistics`
            statistics related to duration of match in time-series
        """
        return self._duration_statistics

    @property
    def multi_match_norm_frequency(self):
        """
        Returns
        -------
        int
            provides the total number of matches given a set of sets and a subset, with one
        set possibly matching a subset multiple times.
        """
        return self._j_statistics.multiMatchNormFrequency()

    @property
    def binary_match_norm_frequency(self):
        """
        Returns
        -------
        int
            indicating number of matches in the set, where any number of matches for a given itemset counts as a single
        match
        """
        return self._j_statistics.binaryMatchNormFrequency()

    @property
    def coverage(self):
        """
        Returns
        -------
        float
            The coverage (binary_match_normalized_frequency / original_size) of the set for the FIM itemset
        """
        return self._j_statistics.coverage()

    def __str__(self):
        return self._j_statistics.toString()
