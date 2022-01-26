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

from autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.FrequentSubSequenceStatistics import FrequentSubSequenceStatistics
from autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.ItemSetSequence import ItemSetSequence


class FrequentSubSequence:
    """
    container class to represent a frequent-sub-sequence stored as part of a :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.FrequentSubSequenceModel.FrequentSubSequenceModel`

    Attributes
    ----------

    sequence : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.ItemSetSequence.ItemSetSequence`
        the sequence of item-sets
    sequence_id : int
        the id generated for this sequence
    statistics : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.FrequentSubSequenceStatistics.FrequentSubSequenceStatistics`
        the statistics associated with this sequence
    """
    def __init__(self, j_fss):
        self._j_fss = j_fss
        self._sequence = ItemSetSequence(j_fss.sequence())
        self._statistics = FrequentSubSequenceStatistics(j_fss.statistics())

    @property
    def sequence(self):
        """
        Returns
        -------
        :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.ItemSetSequence.ItemSetSequence`
            the sequence of item-sets
        """
        return self._sequence

    @property
    def sequence_id(self):
        """
        Returns
        -------
        int
            the id generated for this sequence
        """
        return self._j_fss.sequenceID()

    @property
    def statistics(self):
        """
        Returns
        -------
        statistics : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.FrequentSubSequenceStatistics.FrequentSubSequenceStatistics`
            the statistics associated with this sequence
        """
        return self._statistics

    def __str__(self):
        return self._j_fss.toString()
