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

from autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DiscriminatoryItemSetStatistics import DiscriminatoryItemSetStatistics


class DiscriminatoryItemSet:
    """
    container class to represent a discriminatory-itemset stored as part of a :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DiscriminatoryItemSetModel.DiscriminatoryItemSetModel`

    Attributes
    ----------

    item_set : list
        holder of the item-set created by the Discriminatory ItemSet Mining algorithm
    item_set_id : int
        unique identifier for this discriminatory item-set in the :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DiscriminatoryItemSet.DiscriminatoryItemSet`Model
    statistics : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DiscriminatoryItemSetStatistics.DiscriminatoryItemSetStatistics`
        the statistics associated with this item-set
    """
    def __init__(self, j_dis):
        self._j_dis = j_dis

        items = []
        for item in j_dis.itemSet():
            items.append(item)

        self._item_set = items
        self._statistics = DiscriminatoryItemSetStatistics(j_dis.statistics())

    @property
    def statistics(self):
        """
        Returns
        -------
        :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DiscriminatoryItemSetStatistics.DiscriminatoryItemSetStatistics`
            the statistics associated with this item-set
        """
        return self._statistics

    @property
    def item_set(self):
        """
        Returns
        -------
        list
            the item-set created by the Discriminatory ItemSet Mining algorithm
        """
        return self._item_set

    @property
    def item_set_id(self):
        """
        Returns
        -------
        int
            unique identifier for this discriminatory item-set in the :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.DiscriminatoryItemSet.DiscriminatoryItemSet`Model
        """
        return self._j_dis.itemSetID()

    def __str__(self):
        return self._j_dis.toString()
