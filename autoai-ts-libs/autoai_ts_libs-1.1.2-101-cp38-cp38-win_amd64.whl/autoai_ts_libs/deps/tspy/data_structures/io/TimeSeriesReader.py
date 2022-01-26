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


class TimeSeriesReader:
    """
    interface to represent reading time-series data from a data-source
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def read(self, start, end, inclusive):
        """
        read from a source between start and end

        Parameters
        ----------
        start : int
            start of range (inclusive)
        end : int
            end of range (inclusive)
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        iter
            an iterator to a set of observations between floor(start) and ceiling(end) of our source
        """
        return

    @abc.abstractmethod
    def close(self):
        """
        close the connection to our source
        """
        return

    @abc.abstractmethod
    def start(self):
        """
        start reading data

        Returns
        -------
        int
            get the starting time-tick in the source data
        """
        return

    @abc.abstractmethod
    def end(self):
        """
        end reading data

        Returns
        -------
        int
            get the ending time-tick in the source data
        """
        return
