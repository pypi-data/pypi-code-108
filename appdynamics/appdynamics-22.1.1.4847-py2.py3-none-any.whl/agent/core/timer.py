# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Timers for the AppDynamics Python agent.

This provides a convenient way of keeping track of how long some block or
process takes to run.

Using Timers
------------

To create a timer, pass it a function that takes no arguments and returns the
current time in milliseconds:

    >>> time_ms = lambda: int(time.time() * 1000)
    >>> timer = Timer(time_ms)

A timer can be manually started:

    >>> timer.start()

You can retrieve when the timer was last started:

    >>> timer.start_time_ms

If the timer has never been started, this returns `None`. After a timer has
started, you can retrieve how long its been active in milliseconds:

    >>> sleep(0.01)
    >>> timer.duration_ms
    10

A timer can be stopped to freeze its duration:

    >>> timer.end()
    >>> timer.duration_ms
    10

Once the timer has been stopped, the duration is no longer updated:

    >>> sleep(0.01)
    >>> timer.duration_ms
    10

The time that the timer was last stopped can be retrieved:

    >>> timer.stop_time_ms

You may re-start a timer that has been stopped. Doing so updates the start
time and adds to the duration for the time that the timer is running.

"""

from __future__ import unicode_literals


class Timer(object):
    """A timer that tracks the total duration of how long it has been active.

    For use in the agent, timers can be created using the `Agent.timer()`
    factory method.

    A timer is active immediately upon it being started with its `start`
    method until it is stopped with its `stop` method. A timer can be started
    and stopped multiple times; its duration will be the sum of the durations
    for which it was active.

    A timer may be used as context manager via the Python `with` keyword. The
    timer is automatically started upon entering the block and ended when the
    block exits.

    Parameters
    ----------
    time_fn : callable
        A callable that takes zero arguments and returns the current time as
        an int/long in milliseconds.
    expiration_ms : int, optional
        If passed, the timer is said to be expired if the timer's duration
        exceeds this value. The default is `None`, indicating the timer never
        expires.

    Attributes
    ----------
    active : bool
        True if the timer is currently active.
    expired : bool
        If this timer has an expiration timer, true if the timer has
        expired, else false.
    expiration_ms : int or None
        If not None, the timer's "expired" flag will be true if its duration
        is greater than or equal to this value.
    start_time_ms : int
        The timestamp (in milliseconds) of when the timer was last started.
    stop_time_ms : int
        The timestamp (in milliseconds) of when the timer was last stopped.
    duration_ms : int
        The total time (in milliseconds) this timer has been active.
    has_stopped : bool
        True if the timer was formerly active and is not currently active.
        If the timer was never started, then false. If the timer is currently
        active, then false.

    """

    def __init__(self, time_fn, expiration_ms=None):
        super(Timer, self).__init__()
        self.time = time_fn
        self.reset()
        self.expiration_ms = expiration_ms

    @property
    def active(self):
        return self._active

    @property
    def has_stopped(self):
        return bool(self._start is not None and not self._active)

    @property
    def expired(self):
        return self.expiration_ms is not None and self.duration_ms >= self.expiration_ms

    @property
    def start_time_ms(self):
        return self._start

    @property
    def stop_time_ms(self):
        return self._end

    @property
    def duration_ms(self):
        if self._start is None:  # Never started
            return None

        if self._active:
            return self._duration_ms + self.since_start_ms
        else:
            return self._duration_ms

    @property
    def since_start_ms(self):
        if self._start is None:  # Never started
            return 0

        return self.time() - self._start

    def reset(self):
        """Reset the timer to its initial state (as if it had never been active).

        """
        self._duration_ms = 0
        self._start = None
        self._end = None
        self._active = False

    def start(self, expiration_ms=None):
        """Start the timer.

        If the timer is already active, this does nothing.

        Other Parameters
        ----------------
        expiration_ms : int, optional
            If specified, this sets the timer's expiration time. If `None`,
            the default, the timer's existing expiration time, if any, is
            left intact.

        """
        if self._active:
            return self

        if expiration_ms is not None:
            self.expiration_ms = expiration_ms

        self._start = self.time()
        self._active = True
        return self

    def stop(self):
        """Stop the timer.

        If the timer is not currently active, this does nothing.

        """
        if self._active:
            self._end = self.time()
            self._duration_ms += self._end - self._start
            self._active = False
        return self.duration_ms

    __enter__ = start

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
