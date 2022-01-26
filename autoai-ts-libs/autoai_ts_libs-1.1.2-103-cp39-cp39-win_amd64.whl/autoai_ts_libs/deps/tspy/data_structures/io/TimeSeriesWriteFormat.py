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

class TimeSeriesWriteFormat:
    """
    Format which denotes how to write to a data-source
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, observations, encode_value_func, options):
        """
        Given a collection of observations, a value encoder and options created from time-series-writer,
        write to an outside data-source

        Parameters
        ----------
        observations : :class:`~autoai_ts_libs.deps.tspy.io.ObservationCollection.ObservationCollection`
            the in-memory observations to write to an outside data-source
        encode_value_func : func
            function to encode a value to a String, by default __str__ is used
        options : dict
            key-value string pair in map of options to be used in writing
        """
        pass
