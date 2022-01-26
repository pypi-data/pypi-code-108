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

import abc


class BinaryTransform:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def evaluate(self, time_series_left, time_series_right, start, end, inclusive_bounds):
        """given a data_structures return a realized time series (ObservationCollection)"""
        return
