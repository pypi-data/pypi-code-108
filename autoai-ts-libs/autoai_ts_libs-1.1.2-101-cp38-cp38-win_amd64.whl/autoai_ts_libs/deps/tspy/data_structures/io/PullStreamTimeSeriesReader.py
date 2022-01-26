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

from autoai_ts_libs.deps.tspy.data_structures import utils


class PullStreamTimeSeriesReader(object):
    """
    interface to represent reading stream-time-series data at motion from a data-source where data is being pulled to
    the reader
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        self._tsc = get_or_create()
        self._j_reader = self._tsc._jvm.com.ibm.research.time_series.streaming.io.PythonPullStreamTimeSeriesReader(
            utils.UnaryMapFunctionResultingInOptional(self._tsc, self.parse),
            utils.IteratorMessageSupplier(self._tsc, self.poll)
        )

    def _parse(self, message):
        return self._j_reader.parse(message)

    def _read(self):
        return self._j_reader.read()

    @abc.abstractmethod
    def parse(self, message):
        """
        parse a message

        Parameters
        ----------
        message : Any
            a message

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.Observation.Observation`
            a single observation or None if parsing has failed
        """
        return

    @abc.abstractmethod
    def poll(self):
        """
        poll for the latest list of messages from your source

        Returns
        -------
        list
            a list of messages
        """
        return
