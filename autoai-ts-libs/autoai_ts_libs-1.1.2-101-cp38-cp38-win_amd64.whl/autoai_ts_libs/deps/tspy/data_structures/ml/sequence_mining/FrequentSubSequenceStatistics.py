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


class FrequentSubSequenceStatistics:
    """
    Container class representing Frequent-Sub-Sequence statistics

    This class provides various statistics on the FSM subsequence, this is associated with a FSM subsequence.
    Statistics range from (1) Coverage, (2) Inter-arrival
    statistics (which can be used to analyze time spent between transitions from one element to another in the
    subsequence.

    Attributes
    ----------
    original_size : int
        indicating the number of sequences that match the FSM subsequence
    binary_match_normalized_frequency : int
        indicating number of matches, where any number of matches for a given sequence counts as a single match
    coverage : float
        The coverage (binary_match_normalized_frequency / original_size) of the set for the FSM subsequence
    inter_arrival_statistics : list
        inter-arrival timing statistics for the FSM sequence
    """

    def __init__(self, j_statistics):
        self._j_statistics = j_statistics
        inter_arrival_statistics = []
        for j_iat in self._j_statistics.interArrivalStatistics():
            inter_arrival_statistics.append(InterArrivalStatistics(j_iat))
        self._inter_arrival_statistics = inter_arrival_statistics

    @property
    def original_size(self):
        """
        Returns
        -------
        int
            indicating the number of sequences that match the FSM subsequence
        """
        return self._j_statistics.originalSize()

    @property
    def binary_match_normalized_frequency(self):
        """
        Returns
        -------
        int
            indicating number of matches, where any number of matches for a given sequence counts as a single match
        """
        return self._j_statistics.binaryMatchNormalizedFrequency()

    @property
    def coverage(self):
        """
        Returns
        -------
        float
            The coverage (binary_match_normalized_frequency / original_size) of the set for the FSM subsequence
        """
        return self._j_statistics.coverage()

    @property
    def inter_arrival_statistics(self):
        """
        Returns
        -------
        list
            inter-arrival timing statistics for the FSM sequence
        """
        return self._inter_arrival_statistics

    def __str__(self):
        return self._j_statistics.toString()
