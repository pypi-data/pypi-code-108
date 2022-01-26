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


class TimeSeriesWriter:
    """
    Builder pattern used for writing a time-series to an outside data-source

    Notes
    ----------
    A time-series-writer has a few components:
        - observations: the in-memory observations to write to an outside data-source
        - options: key-value string pair in map of options to be used in writing
        - value-encoder: function to encode a value to a String, by default __str__ is used

    This class works as follows:
        - builds a blank time-series-writer that only contains observations
        - set options and value-encoder (optional)
        - save to data-source (using a time-series-write-format) given options and value-encoder
    """
    def __init__(self, tsc, j_time_series_writer):
        self._tsc = tsc
        self._j_time_series_writer = j_time_series_writer

    def encode_value(self, value_encoder):
        """
        set function to encode a value to a string when writing

        Parameters
        ----------
        value_encoder : func
            function to encode a value to a string when writing

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.io.TimeSeriesWriter.TimeSeriesWriter`
            this time-series-writer
        """
        self._j_time_series_writer.encodeValue(utils.UnaryMapFunction(self._tsc, value_encoder))
        return self

    def option(self, key, value):
        """
        set an option for this time-series-writer

        Parameters
        ----------
        key : str
            option key
        value : Any
            option value

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.io.TimeSeriesWriter.TimeSeriesWriter`
            this time-series-writer
        """
        self._j_time_series_writer.option(key, value)
        return self

    def options(self, **kwargs):
        """
        set multiple options for this time-series-writer

        Parameters
        ----------
        kwargs : key-value varargs
            key-value options as varargs

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.io.TimeSeriesWriter.TimeSeriesWriter`
            this time-series-writer
        """
        for key, value in kwargs.items():
            self._j_time_series_writer.option(key, value)
        return self

    def csv(self, path):
        """
        save as csv

        Parameters
        ----------
        path : str
            file path to save to
        """
        self._j_time_series_writer.csv(path)

    def object_file(self, path):
        """
        save as object-file

        Parameters
        ----------
        path : str
            file path to save to
        """
        self._j_time_series_writer.objectFile(path)

    def save(self, time_series_write_format):
        """
        save to a user-defined time-series-write-format

        Parameters
        ----------
        time_series_write_format : :class:`~autoai_ts_libs.deps.tspy.io.TimeSeriesWriteFormat.TimeSeriesWriteFormat`
            the time-series write format
        """
        self._j_time_series_writer.save(utils.JavaTimeSeriesWriteFormat(self._tsc, time_series_write_format))
