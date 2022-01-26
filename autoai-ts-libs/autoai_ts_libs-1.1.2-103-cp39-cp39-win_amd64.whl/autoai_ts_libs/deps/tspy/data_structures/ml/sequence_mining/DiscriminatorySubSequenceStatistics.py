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

from autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.InterArrivalStatistics import InterArrivalStatistics


class DiscriminatorySubSequenceStatistics:
    """
    Container class representing Discriminatory-Sub-Sequence statistics

    This class provides various statistics on the DSM subsequence, this is associated with a DSM subsequence.
    Statistics range from (1) Coverage, (2) Lift, (3) Inter-arrival
    statistics (which can be used to analyze time spent between transitions from one element to another in the
    subsequence.

    Attributes
    ----------
    original_size_left : int
        indicating the number of sequences in L-set that match the DSM subsequence
    original_size_right : int
        indicating the number of sequences in R-set that match the DSM subsequence
    binary_match_normalized_frequency_left : int
        indicating number of matches in the L-set, where any number of matches for a given sequence counts as a single
        match
    binary_match_normalized_frequency_right : int
        indicating number of matches in the R-set, where any number of matches for a given sequence counts as a single
        match
    coverage_left : float
        The coverage (binary_match_normalized_frequency_left / original_size_left) of the L-set for the DSM subsequence
    coverage_right : float
        The coverage (binary_match_normalized_frequency_right / original_size_right) of the R-set for the DSM
        subsequence
    lift : float
        a measure indicating how many times the DSM subsequence is more likely to occur in L-set than R-set.
    inter_arrival_statistics : list
        inter-arrival timing statistics for the DSM sequence
    """

    def __init__(self, j_statistics):
        self._j_statistics = j_statistics
        inter_arrival_statistics = []
        for j_iat in self._j_statistics.interArrivalStatistics():
            inter_arrival_statistics.append(InterArrivalStatistics(j_iat))
        self._inter_arrival_statistics = inter_arrival_statistics

    @property
    def original_size_left(self):
        """
        Returns
        -------
        int
            indicating the number of sequences in L-set that match the DSM subsequence
        """
        return self._j_statistics.originalSizeLeft()

    @property
    def original_size_right(self):
        """
        Returns
        -------
        int
            indicating the number of sequences in R-set that match the DSM subsequence
        """
        return self._j_statistics.originalSizeRight()

    @property
    def binary_match_normalized_frequency_left(self):
        """
        Returns
        -------
        int
            indicating number of matches in the L-set, where any number of matches for a given sequence counts as a
            single match
        """
        return self._j_statistics.binaryMatchNormalizedFrequencyLeft()

    @property
    def binary_match_normalized_frequency_right(self):
        """
        Returns
        -------
        int
            indicating number of matches in the R-set, where any number of matches for a given sequence counts as a
            single match
        """
        return self._j_statistics.binaryMatchNormalizedFrequencyRight()

    @property
    def coverage_left(self):
        """
        Returns
        -------
        float
            The coverage (binary_match_normalized_frequency_left / original_size_left) of the L-set for the DSM
            subsequence
        """
        return self._j_statistics.coverageLeft()

    @property
    def coverage_right(self):
        """
        Returns
        -------
        float
            The coverage (binary_match_normalized_frequency_right / original_size_right) of the R-set for the DSM
        subsequence
        """
        return self._j_statistics.coverageRight()

    @property
    def lift(self):
        """
        Returns
        -------
        float
            a measure indicating how many times the DSM subsequence is more likely to occur in L-set than R-set.
        """
        return self._j_statistics.lift()

    @property
    def inter_arrival_statistics(self):
        """
        Returns
        -------
        list
            inter-arrival timing statistics for the DSM sequence
        """
        return self._inter_arrival_statistics

    def __str__(self):
        return self._j_statistics.toString()
