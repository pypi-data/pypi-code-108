#!/usr/bin/python
"""\
@file   timing.py
@author Nat Goodspeed
@date   2014-09-14
@brief  Track and display time values, e.g. for long-running operations

Copyright (c) 2014, Nat Goodspeed
"""

import datetime
import time

# Each pair is the name of a unit, with the number it takes to make one
# of the next-larger unit.
TIME_UNITS = (0, "weeks"), (7, "days"), (24, "hours"), (60, "minutes"), (60, "seconds")

# --------------------------------- duration ---------------------------------
# Human-readable string reporting a duration in seconds, e.g. "3 weeks, 1 days"
def duration(seconds, levels=None):
    # collect (number, name) pairs in this list
    out = []
    rest = int(seconds)
    # Skip the largest time unit: since there's no larger time unit, we don't
    # need to divide by anything; that entry only provides the name for
    # whatever's left over. Reverse the list, working from seconds on up.
    for dividend, name in reversed(TIME_UNITS[1:]):
        # split off how many of this next-larger unit remain in 'rest'
        rest, remainder = divmod(rest, dividend)
        # prepend onto 'out' a new pair with that quantity and unit name
        out.insert(0, (remainder, name))
    # Whatever's left over, prepend that with the name of the largest unit.
    out.insert(0, (rest, TIME_UNITS[0][1]))
    # Filter the list, keeping only pairs with nonzero quantities.
    out = [pair for pair in out if pair[0]]
    if not out:
        # If the filtered list is entirely empty, force in a pair with the
        # original input number and the name of the smallest unit.
        # Since this case is engaged when the original input < 1, preformat
        # seconds -- otherwise we end up with an absurd number of fractional
        # places.
        out.append(("%.3f" % seconds, TIME_UNITS[-1][1]))
    # Format each pair: (33, "seconds") becomes "33 seconds". Join all those
    # with commas, but first truncate to number of desired levels.
    # (list[:None] preserves the whole list, no truncation.)
    return ", ".join(["%s %s" % pair for pair in out[:levels]])

# -------------------------------- pickUnits ---------------------------------
def pickUnits(value, div, *units):
    """Call this like:
    pickUnits(timeDiff, 60, "hours", "minutes", "seconds")
    or
    pickUnits(byteSize, 1024, "gb", "mb", "kb", "b")
    Returns a string formatted like "12.2 minutes" or "3.1 mb".
    The last of the units strings is associated with div^0, the next one with
    div^1, the next with div^2, etc. Picks the highest specified unit for
    which value/div^power has a nonzero integer part, or the lowest unit for
    value < 1.
    """
    # defend against NO units
    if not units:
        return "%.1f" % value

    # Given units == ("hours", "minutes", "seconds"), reverse it to
    # ("seconds", "minutes", "hours"). Then use zip to associate each unit
    # with an appropriate power of the low-order unit:
    # ((1, "seconds"), (60, "minutes"), (3600, "hours"))
    # Finally reverse that sequence again:
    # ((3600, "hours"), (60, "minutes"), (1, "seconds"))
    # Then walk those pairs to find the highest-order unit that scales the
    # original value to a nice integer value. Put differently, if value is
    # 120, we're not interested in describing it as 1/30th of an hour -- it
    # makes much more sense to call it 2 minutes.
    for power, unit in reversed(zip(_powers(div), reversed(units))):
        quotient = float(value)/power
        if int(quotient):
            break
    # Now we know which unit to use to describe our value. Note that if we
    # fall out of the loop without hitting an integer quotient, the low-order
    # unit is appropriate. That is, if value is 0.5, it's better to describe
    # it as 0.5 seconds than as 1/120th of a minute.
    return "%.1f %s" % (quotient, unit)

def _powers(base):
    """generate an infinite series of powers of the specified base"""
    power = 1
    while True:
        yield power
        power *= base

# ---------------------------------- Timer -----------------------------------
class Timer(object):
    """
    Usage:

    with Timer() as timer:
        # some operation...
    timer.time()     # elapsed time, in float seconds
    timer.duration() # string representation using duration() above
    timer.units()    # string representation using pickUnits() above
    timer.format(strftime format string) # custom formatting
    """
    def __enter__(self):
        self.start = time.time()
        self.end   = None
        return self

    def __exit__(self, type, value, tb):
        self.end = time.time()
        # We don't care whether an exception occurred. Don't swallow it.
        return False

    def time(self):
        # You can call any of our public-facing methods within the 'with'
        # block to get elapsed time. Once the 'with' block exits (__exit__()
        # has been called), all we present is the duration of the 'with'
        # block.
        return (self.end or time.time()) - self.start

    def duration(self, *args, **kwds):
        # believe it or not, this works
        return duration(self.time(), *args, **kwds)

    def units(self, *args, **kwds):
        if not (args or kwds):
            args = (60, "hours", "minutes", "seconds")
        return pickUnits(self.time(), *args, **kwds)

    def format(self, format):
        # If we simply take self.time() (elapsed time in seconds) as a Unix
        # timestamp and pass it to format_time(), we get a peculiar result in
        # that localtime() adjusts for UTC. To support non-silly results for
        # any strftime() formats other than %H, %M, %S, get today at midnight
        # in POSIX time and add that to self.time().
        today = time.mktime(datetime.date.today().timetuple())
        return format_time(format, today + self.time())

# ------------------------------- format_time --------------------------------
def format_time(format, t):
    """
    strftime() formatting for a Unix timestamp, such as ProgressTimer.start or
    finish.
    """
    return time.strftime(format, time.localtime(t))

# ------------------------------ ProgressTimer -------------------------------
class ProgressTimer(object):
    """
    This class tracks the time at which it's instantiated (or every time
    it's reset to 0, or every time you set a new total) and the amount
    processed, and guesses several time-related attributes. Naturally, the
    guesses get better as we get closer to being done.

    Update by assigning to count or to total, or by calling bump() or reset().

    Public attributes:

    count:     number of items processed so far (from caller)
    total:     total number of items to process (from caller)

    start:     time of last reset (time.time() Unix timestamp)
    elapsed:   time since start (float seconds)
    finish:    time at which we EXPECT to complete (time.time() timestamp)
    totaltime: finish minus start (float seconds)
    timeleft:  finish minus now (float seconds)
    """
    def __init__(self, total, count=0, start=None):
        """
        Don't pass total=0. That's just wrong.
        """
        self.reset(total, count, start)

    def reset(self, total=None, count=None, start=None):
        if total is not None:
            self._total = total
        if count is not None:
            self._count = count

        # all time attributes
        self.start = start if start is not None else time.time()
        self.finish = self.start
        self.elapsed = 0
        self.totaltime = 0
        self.timeleft = 0

        # in case of nonzero count
        self._update()

    # ---------------------------- total property ----------------------------
    def _get_total(self):
        return self._total

    def _set_total(self, total):
        if self._total != total:
            self.reset(total)

    total = property(_get_total, _set_total)

    # ---------------------------- count property ----------------------------
    def _get_count(self):
        return self._count

    def _set_count(self, count):
        if self._count != count:
            self._count = count
            if count == 0:
                self.reset(count=count)
            else:
                self._update()

    count = property(_get_count, _set_count)

    # -----------------------------------  -----------------------------------
    def bump(self, by=1):
        # leverage the property to call _set_count() for this
        self.count += by

    def _update(self):
        self.elapsed = time.time() - self.start
        if self._count:
            self.totaltime = self.elapsed * (float(self._total)/self._count)
            self.finish    = self.start + self.totaltime
            self.timeleft  = self.totaltime - self.elapsed
