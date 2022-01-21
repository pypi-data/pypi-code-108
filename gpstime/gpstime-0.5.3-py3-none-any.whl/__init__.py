"""datetime with GPS time support

This module primarily provides functions for converting to/from UNIX
and GPS times, as well as a `gpstime` class that directly inherits
from the builtin `datetime` class, adding additional methods for GPS
time input and output.

Leap seconds are expected to be provided by the core libc Time Zone
Database tzdata.  If for some reason the tzdata leapsecond file is not
available, a local cache of the IETF leap second record will be
maintained:

  https://www.ietf.org/timezones/data/leap-seconds.list

KNOWN BUGS: This module does not currently handle conversions of time
strings describing the actual leap second themselves, which are
usually represented as the 60th second of the minute during which the
leap second occurs.

"""
from datetime import datetime
import warnings
import argparse
import subprocess

from dateutil.tz import tzutc, tzlocal

try:
    from .__version__ import version as __version__
except ModuleNotFoundError:
    try:
        import setuptools_scm
        __version__ = setuptools_scm.get_version(fallback_version='?.?.?')
    # FIXME: fallback_version is not available in the buster version
    # (3.2.0-1)
    except TypeError:
        __version__ = setuptools_scm.get_version()
    except LookupError:
        __version__ = '?.?.?'

from .leaps import LEAPDATA


##################################################

ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

# UNIX time for GPS 0 (1980-01-06T00:00:00Z)
GPS0 = 315964800

##################################################


def unix2gps(unix):
    """Convert UNIX timestamp to GPS time.

    """
    unix = float(unix)
    gps = unix - GPS0
    for leap in LEAPDATA:
        if leap < GPS0:
            continue
        if unix < leap:
            break
        gps += 1
    return gps


def gps2unix(gps):
    """Convert GPS time to UNIX timestamp.

    """
    gps = float(gps)
    unix = gps + GPS0
    for leap in LEAPDATA:
        if leap < GPS0:
            continue
        if unix < leap:
            break
        unix -= 1
    return unix


##################################################


class GPSTimeException(Exception):
    pass


def cudate(string='now'):
    """Parse date/time string to UNIX timestamp with GNU coreutils date

    """
    cmd = ['date', '+%s.%N', '-d', string]
    try:
        ts = subprocess.check_output(cmd, stderr=subprocess.PIPE).strip()
    except subprocess.CalledProcessError:
        raise GPSTimeException("could not parse string '{}'".format(string))
    return float(ts)


def dt2ts(dt):
    """Return UNIX timestamp for datetime object.

    """
    try:
        dt = dt.astimezone(tzutc())
        tzero = datetime.fromtimestamp(0, tzutc())
    except ValueError:
        warnings.warn("GPS converstion requires timezone info.  Assuming local time...",
                      RuntimeWarning)
        dt = dt.replace(tzinfo=tzlocal())
        tzero = datetime.fromtimestamp(0, tzlocal())
    delta = dt - tzero
    return delta.total_seconds()


##################################################


class gpstime(datetime):
    """GPS-aware datetime class

    An extension of the datetime class, with the addition of methods
    for converting to/from GPS times:

    >>> from gpstime import gpstime
    >>> gt = gpstime.fromgps(1088442990)
    >>> gt.gps()
    1088442990.0
    >>> gt.strftime('%Y-%m-%d %H:%M:%S %Z')
    '2014-07-03 17:16:14 UTC'
    >>> gpstime.now().gps()
    1133737481.204008

    In addition a natural language parsing `parse` classmethod returns
    a gpstime object for a arbitrary time string:

    >>> gpstime.parse('2014-07-03 17:16:14 UTC').gps()
    1088442990.0
    >>> gpstime.parse('2 days ago').gps()
    1158440653.553765

    """
    def __new__(cls, *args):
        return datetime.__new__(cls, *args)

    @classmethod
    def fromdatetime(cls, datetime):
        """Return gpstime object from datetime object"""
        tzinfo = datetime.tzinfo
        if tzinfo is None:
            tzinfo = tzlocal()
        cls = gpstime(
            datetime.year, datetime.month, datetime.day,
            datetime.hour, datetime.minute, datetime.second, datetime.microsecond,
            tzinfo,
        )
        return cls

    @classmethod
    def fromgps(cls, gps):
        """Return gpstime object corresponding to GPS time."""
        gt = cls.utcfromtimestamp(gps2unix(gps))
        # HACK: in python3, utcfromtimestamp() seems to floor instead
        # of round the microseconds.  this causes round trips to fail.
        # manually fix microseconds here to the rounded value instead.
        ms = int(round(abs(gps - int(gps))*1000000))
        return gt.replace(microsecond=ms, tzinfo=tzutc())

    @classmethod
    def parse(cls, string='now'):
        """Parse an arbitrary time string into a gpstime object.

        If string not specified 'now' is assumed.  Strings that can be
        cast to float are assumed to be GPS times.  Prepend '@' to a
        float to specify a UNIX timestamp.

        This parse uses the natural lanuage parsing abilities of the
        GNU coreutils 'date' utility.  See "DATE STRING" in date(1)
        for information on possible date/time descriptions.

        """
        if string == 'now':
            return cls.now().replace(tzinfo=tzlocal())
        try:
            gps = float(string)
        except ValueError:
            gps = None
        except TypeError:
            raise TypeError("Time specification must be a string, not {!s}".format(type(string)))
        if gps is not None:
            return cls.fromgps(gps)
        try:
            ts = cudate(string)
        except GPSTimeException:
            # try again in case this was an ISO string using
            # underscore instead of T as the separator
            ts = cudate(string.replace('_', 'T'))
        return cls.fromtimestamp(ts).replace(tzinfo=tzlocal())

    tconvert = parse

    def timestamp(self):
        """Return UNIX timestamp (seconds since epoch)."""
        return dt2ts(self)

    def gps(self):
        """Return GPS time as a float."""
        return unix2gps(self.timestamp())

    def iso(self):
        """Return time in standard UTC ISO format."""
        return self.astimezone(tzutc()).strftime(ISO_FORMAT)


def tconvert(string='now', form='%Y-%m-%d %H:%M:%S.%f %Z'):
    """Reimplementation of LIGO "tconvert" binary behavior

    Given a GPS time string, return the date/time string with the
    specified format.  Given a date/time string, return the GPS time.

    This just uses the gpstime.parse() method internally.

    """
    gt = gpstime.parse(string)
    try:
        float(string)
        return gt.strftime(form)
    except ValueError:
        return gt.gps()


def gpsnow():
    """Return current GPS time as a float.

    """
    return gpstime.utcnow().replace(tzinfo=tzutc()).gps()


parse = gpstime.parse


class GPSTimeParseAction(argparse.Action):
    """gpstime argparse argumention parser Action.

    Parses an arbitrary date/time string into a gpstime object.

    """
    def __call__(self, parser, namespace, values, option_string=False):
        # FIXME: support parsing argparse.REMAINDER values list into a
        # single string
        if isinstance(values, list):
            values = ' '.join(values)
        try:
            gps = parse(values)
        except GPSTimeException:
            parser.error("Could not parse date/time string '{}'".format(values))
        setattr(namespace, self.dest, gps)
