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

from autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSetStatistics import FrequentItemSetStatistics


class FrequentItemSet:
    """
    container class to represent a frequent-itemset stored as part of a :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSetModel.FrequentItemSetModel`

    Attributes
    ----------

    item_set : list
        holder of the item-set created by the Frequent ItemSet Mining algorithm
    item_set_id : int
        unique identifier for this frequent item-set in the :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSetModel.FrequentItemSetModel`
    statistics : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSetStatistics.FrequentItemSetStatistics`
        the statistics associated with this item-set
    """
    def __init__(self, j_fis):
        self._j_fis = j_fis

        items = []
        for item in j_fis.itemSet():
            items.append(item)

        self._item_set = items
        self._statistics = FrequentItemSetStatistics(j_fis.statistics())

    @property
    def statistics(self):
        """
        Returns
        -------
        :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSetStatistics.FrequentItemSetStatistics`
            the statistics associated with this item-set
        """
        return self._statistics

    @property
    def item_set(self):
        """
        Returns
        -------
        list
            holder of the item-set created by the Frequent ItemSet Mining algorithm
        """
        return self._item_set

    @property
    def item_set_id(self):
        """
        Returns
        -------
        int
            unique identifier for this frequent item-set in the :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSetModel.FrequentItemSetModel`
        """
        return self._j_fis.itemSetID()

    def __str__(self):
        return self._j_fis.toString()
