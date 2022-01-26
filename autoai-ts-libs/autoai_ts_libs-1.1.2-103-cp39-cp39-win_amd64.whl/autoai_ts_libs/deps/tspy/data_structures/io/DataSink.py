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


class DataSink(object):
    """
    interface to represent a data-sink for a single time-series
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def dump(self, observations):
        """
        dump an observation-collection to an output source
        """
        pass
