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

from autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining import FISModelFactory, ItemSetMatcherFactory, DISModelFactory


class Factory(object):

    def __init__(self, tsc):
        self._tsc = tsc

    @property
    def fim_model(self):
        return FISModelFactory.Factory(self._tsc)

    @property
    def dim_model(self):
        return DISModelFactory.Factory(self._tsc)

    @property
    def item_set_matchers(self):
        return ItemSetMatcherFactory.Factory(self._tsc)
