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

class ItemSetSequence:
    """
    container class representing a sequence of item-sets

    Attributes
    ----------

    sequence : list
        sequence of itemsets
    """
    def __init__(self, j_itemset_sequence):
        self._j_itemset_sequence = j_itemset_sequence
        sequence = []
        for itemset in j_itemset_sequence.itemsets():
            itemset_i = []
            for item in itemset:
                itemset_i.append(item)
            sequence.append(itemset_i)
        self._sequence = sequence

    def __iter__(self):
        return self._sequence.__iter__()

    @property
    def sequence(self):
        """
        Returns
        -------
        list
            the underlying sequence of itemsets
        """
        return self._sequence

