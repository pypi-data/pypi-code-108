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

from autoai_ts_libs.deps.tspy.data_structures import utils


class Factory(object):

    def __init__(self, tsc):
        self._tsc = tsc

    def remove_consecutive_duplicate_values(self):
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.duplicate.DuplicateTransformers.removeConsecutiveDuplicateValues()

    def combine_duplicate_time_ticks(self, combine_strategy):
        if hasattr(combine_strategy, '__call__'):
            return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.duplicate.DuplicateTransformers.combineDuplicateTimeTicks(
                utils.UnaryMapFunction(self._tsc, combine_strategy)
            )
        else:
            return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.duplicate.DuplicateTransformers.combineDuplicateTimeTicks(combine_strategy)
