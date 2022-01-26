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


class DiscriminatoryItemSetStatistics:
    """
    container class representing Discriminatory-Itemset Statistics

    This class provides various statistics on the item-set, this is associated with a Discriminatory ItemSet Mining
    Algorithm. Statistics range from (1) Coverage, (2) Lift, (3) Length statistics

    Attributes
    ----------
    original_size_left : int
        indicating the number of sequences in L-set that match the itemset
    original_size_right : int
        indicating the number of sequences in R-set that match the itemset
    duration_statistics : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DurationStatistics.DurationStatistics`
        statistics related to duration of match in time-series
    binary_match_normalized_frequency_left : int
        indicating number of matches in the L-set, where any number of matches for a given itemset counts as a single
        match
    binary_match_normalized_frequency_right : int
        indicating number of matches in the R-set, where any number of matches for a given itemset counts as a single
        match
    coverage_left : float
        The coverage (binary_match_normalized_frequency_left / original_size_left) of the L-set for the DIM itemset
    coverage_right : float
        The coverage (binary_match_normalized_frequency_right / original_size_right) of the R-set for the DIM
        itemset
    lift : float
        a measure indicating how many times the DIM itemset is more likely to occur in L-set than R-set.
    """

    def __init__(self, j_statistics):
        self._j_statistics = j_statistics
        self._duration_statistics = DurationStatistics(j_statistics.durationStatistics())

    @property
    def original_size_left(self):
        """
        Returns
        -------
        int
            the number of sequences in L-set that match the itemset
        """
        return self._j_statistics.originalSizeLeft()

    @property
    def original_size_right(self):
        """
        Returns
        -------
        int
            the number of sequences in R-set that match the itemset
        """
        return self._j_statistics.originalSizeRight()

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
    def binary_match_norm_frequency_left(self):
        """
        Returns
        -------
        int
            indicating number of matches in the L-set, where any number of matches for a given itemset counts as a
            single match
        """
        return self._j_statistics.binaryMatchNormFrequencyLeft()

    @property
    def binary_match_norm_frequency_right(self):
        """
        Returns
        -------
        int
            indicating number of matches in the R-set, where any number of matches for a given itemset counts as a
            single match
        """
        return self._j_statistics.binaryMatchNormFrequencyRight()

    @property
    def coverage_left(self):
        """
        Returns
        -------
        float
            The coverage (binary_match_normalized_frequency_left / original_size_left) of the L-set for the DIM itemset
        """
        return self._j_statistics.coverageLeft()

    @property
    def coverage_right(self):
        """
        Returns
        -------
        float
            The coverage (binary_match_normalized_frequency_right / original_size_right) of the R-set for the DIM
        itemset
        """
        return self._j_statistics.coverageRight()

    @property
    def lift(self):
        """
        Returns
        -------
        float
            a measure indicating how many times the DIM itemset is more likely to occur in L-set than R-set
        """
        return self._j_statistics.lift()

    def __str__(self):
        return self._j_statistics.toString()
