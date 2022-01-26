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

import datetime

class TRS:
    """
    Time reference system (TRS) is a local, regional or global system used to identify time. A time reference system
    defines a specific projection for forward and reverse mapping between timestamp and its numeric representation. A
    common example that most of us are familiar with is UTC time, which maps a timestamp (Jan 1, 2019 12am midnight GMT)
    into a 64-bit integer value (1546300800000) that captures the number of milliseconds that have elapsed since
    Jan 1, 1970 12am (midnight) GMT. Generally speaking, the timestamp value is better suited for human readability,
    while the numeric representation is better suited for machine processing.

    Attributes
    ----------
    granularity : datetime.timedelta
        granularity that captures time-tick granularity (e.g., 1 minute)
    start_time : datetime
        start-time that captures an offset (e.g., 1st Jan 2019 12am midnight US Eastern Daylight Savings Time) to the
        start time of the time-series)

    Notes
    -----
    A timestamp is mapped into a numeric representation by computing the number of elapsed time-ticks since the
    offset. A numeric representation is scaled by the time-tick and shifted by the offset when it is mapped back to a
    timestamp.

    forward + reverse projections may be lossy. For instance, if the true time granularity of a
    time-series is in seconds, then forward and reverse mapping of timestamps 9:00:01 and 9:00:02 (to be read
    as hh:mm:ss) to a time-tick of one minute would result in timestamps 9:00:00 and 9:00:00 (respectively). In this
    example a time-series whose granularity is in seconds is being mapped to minutes and thus the reverse
    mapping looses information. However, the mapped granularity is higher than the granularity of the input
    time-series (more specifically if the time-series granularity is an integral multiple of the mapped
    granularity) then the forward + reverse projection is guaranteed to be lossless. For example, mapping a
    time-series whose granularity is in minutes to seconds and reverse projecting it to minutes would result
    in lossless reconstruction of the timestamps.

    By default, Granularity is one millisecond, and Start-Time is 1st Jan 1970 00:00:00
    """
    def __init__(self, tsc, granularity, start_time, j_trs=None):
        self._tsc = tsc

        self._granularity = granularity
        self._start_time = start_time

        if self._start_time.tzinfo is None or self._start_time.tzinfo.utcoffset(
                self._start_time) is None:  # this is a naive datetime, must make it aware
            self._start_time = self._start_time.replace(tzinfo=datetime.timezone.utc)

        if j_trs is None:
            j_time_tick = self._tsc._jvm.java.time.Duration.ofMillis(
                int(((granularity.microseconds + (
                        granularity.seconds + granularity.days * 24 * 3600) * 10 ** 6) / 10 ** 6) * 1000)
            )

            j_zdt = self._tsc._jvm.java.time.ZonedDateTime.parse(
                str(self._start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
                self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
            )

            self._j_trs = self._tsc._jvm.com.ibm.research.time_series.core.utils.TRS.of(j_time_tick, j_zdt)
        else:
            self._j_trs = j_trs

    @property
    def granularity(self):
        """
        Returns
        -------
        granularity : datetime.timedelta
            granularity that captures time-tick granularity (e.g., 1 minute)
        """
        return self._granularity

    @property
    def start_time(self):
        """
        Returns
        -------
        start_time : datetime
            start-time that captures an offset (e.g., 1st Jan 2019 12am midnight US Eastern Daylight Savings Time) to the
            start time of the time-series)
        """
        return self._start_time

    def to_long_lower(self, index):
        """
        get the given time-tick as a millisecond long (lower bound)

        Parameters
        ----------
        index : int
            the time-tick to convert

        Returns
        -------
        int
            a millisecond long
        """
        return self._j_trs.toLongLower(index)

    def to_long_upper(self, index):
        """
        get the given time-tick as a millisecond long (upper bound)

        Parameters
        ----------
        index : int
            the time-tick to convert

        Returns
        -------
        int
            a millisecond long
        """
        return self._j_trs.toLongUpper(index)

    def to_index(self, time):
        """
        get the given millisecond long as a time-tick index

        Parameters
        ----------
        time : int or datetime
            the time to convert to an index

        Returns
        -------
        int
            a time-tick index
        """
        if isinstance(time, datetime.datetime):
            if time.tzinfo is None or time.tzinfo.utcoffset(time) is None:  # this is a naive datetime, must make it aware
                time = time.replace(tzinfo=datetime.timezone.utc)

            j_zdt = self._tsc._jvm.java.time.ZonedDateTime.parse(
                str(time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
                self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
            )
            return self._j_trs.toIndex(j_zdt)
        else:
            return self._j_trs.toIndex(time)

    def __str__(self):
        return self._j_trs.toString()
