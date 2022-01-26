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

class InterArrivalStatistics:
    """
    This is a deeper statistics holder class that maintains the inter-arrival times, where inter-arrival time is the time elapsed
    between two consecutive events in the subsequence. For every consecutive pair of events in a sequence, one inter-arrival
    statistics object is maintained. The values are across all the matching sequences for that single step in the subsequence.

    For example, if the subsequence is {a,b,c}, the interarrival statistics are maintained for {a,b} and {b,c}.

    Attributes
    ----------
    min : int
        Minimum inter-arrival time across all the sequences that match the subsequence
    max : int
        Maximum inter-arrival time across all the sequences that match the subsequence
    sum : int
        Sum of inter-arrival time across all the sequences that match the subsequence
    count : int
        Number of sequences that matched this subsequence
    average : float
        average inter-arrival-time across all inter-arrival-times
    sd : float
        standard deviation across all inter-arrival-times
    """

    def __init__(self, j_iat):
        self._j_iat = j_iat

    @property
    def min(self):
        """
        Returns
        -------
        int
            Minimum inter-arrival time across all the sequences that match the subsequence
        """
        return self._j_iat.min()

    @property
    def max(self):
        """
        Returns
        -------
        int
            Maximum inter-arrival time across all the sequences that match the subsequence
        """
        return self._j_iat.max()

    @property
    def sum(self):
        """
        Returns
        -------
        int
            Sum of inter-arrival time across all the sequences that match the subsequence
        """
        return self._j_iat.sum()

    @property
    def count(self):
        """
        Returns
        -------
        int
            Number of sequences that matched this subsequence
        """
        return self._j_iat.count()

    @property
    def average(self):
        """
        Returns
        -------
        float
            average inter-arrival-time across all inter-arrival-times
        """
        return self._j_iat.average()

    @property
    def sd(self):
        """
        Returns
        -------
        float
            standard deviation across all inter-arrival-times
        """
        return self._j_iat.sd()

    def __str__(self):
        return self._j_iat.toString()
