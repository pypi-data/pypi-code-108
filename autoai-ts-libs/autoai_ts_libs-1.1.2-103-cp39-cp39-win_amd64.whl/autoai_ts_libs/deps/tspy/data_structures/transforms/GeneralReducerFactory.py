
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

class Factory(object):

    def __init__(self, tsc):
        self._tsc = tsc

    def count_by_value(self):
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GeneralReducers.countByValue()

    def has_duplicate(self, duplicate_value=None):
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.duplicate.DuplicateReducers.hasDuplicate(duplicate_value)

    def count(self):
        return self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GeneralReducers.count()
