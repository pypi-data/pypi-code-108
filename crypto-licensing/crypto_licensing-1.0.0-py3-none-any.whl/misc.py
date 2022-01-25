# -*- coding: utf-8 -*-

#
# Crypto-licensing -- Cryptographically signed licensing, w/ Cryptocurrency payments
#
# Copyright (c) 2022, Hard Consulting Corporation.
#
# Cpppo is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.  See the LICENSE file at the top of the source tree.
#
# Cpppo is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#

from __future__ import absolute_import, print_function, division
try:
    from future_builtins import zip, map		# Use Python 3 "lazy" zip, map
except ImportError:
    pass

import calendar
import collections
import datetime
import fnmatch
import glob
import logging
import math
import os
import re
import sys
import time

import pytz
try:
    from tzlocal import get_localzone
except ImportError:
    def get_localzone( _root='/' ):
        """No tzlocal; support basic Linux systems with a TZ variable or an /etc/timezone file"""
        # /etc/timezone, ... file?
        for tzbase in ( 'etc/timezone',			# Debian, Ubuntu, ...
                        'etc/sysconfig/clock' ): 	# RedHat, ...
            tzpath		= os.path.join( _root, tzbase )
            if os.path.exists( tzpath ):
                with open( tzpath, 'rb' ) as tzfile:
                    tzname	= tzfile.read().decode().strip()
                if '#' in tzname:
                    # eg. 'Somewhere/Special # The Special Zone'
                    tzname	= tzname.split( '#', 1 )[0].strip()
                if ' ' in tzname:
                    # eg. 'America/Dawson Creek'.  Not really correct, but we'll handle it
                    tzname	= tzname.replace( ' ', '_' )
                return pytz.timezone( tzname )

        raise pytz.UnknownTimeZoneError( 'Can not find any timezone configuration' )

try:
    import reprlib					# noqa: F401
except ImportError:
    import repr as reprlib				# noqa: F401

try:
    xrange(0,1)
except NameError:
    xrange 			= range

try:
    unicode			= unicode
except NameError:
    unicode			= str

try:
    from urllib import urlencode			# noqa: F401
except ImportError:
    from urllib.parse import urlencode			# noqa: F401

__author__                      = "Perry Kundert"
__email__                       = "perry@dominionrnd.com"
__copyright__                   = "Copyright (c) 2022 Dominion R&D Corp."
__license__                     = "Dual License: GPLv3 (or later) and Commercial (see LICENSE)"

"""
Miscellaneous functionality used by various other modules.
"""


# 
# Logging related tooling
# 
log				= logging.getLogger( "misc" )

log_cfg				= {
    "level":	logging.WARNING,
    "datefmt":	'%Y-%m-%d %H:%M:%S',
    #"format":	'%(asctime)s.%(msecs).03d %(threadName)10.10s %(name)-16.16s %(levelname)-8.8s %(funcName)-10.10s %(message)s',
    "format":	'%(asctime)s %(name)-16.16s %(message)s',
}

log_levelmap 			= {
    -2: logging.FATAL,
    -1: logging.ERROR,
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def log_level( adjust ):
    """Return a logging level corresponding to the +'ve/-'ve adjustment"""
    return log_levelmap[
        max(
            min(
                adjust,
                max( log_levelmap.keys() )
            ),
            min( log_levelmap.keys() )
        )
    ]


#
# Python2/3 Compatibility Types
#

# The base class of string types
type_str_base			= basestring if sys.version_info[0] < 3 else str  # noqa: F821

#
# misc.timer
#
# Select platform appropriate timer function
#
if sys.platform == 'win32' and sys.version_info[0:2] < (3,8):
    # On Windows (before Python 3.8), the best timer is time.clock
    timer 			= time.clock
else:
    # On most other platforms the best timer is time.time
    timer			= time.time


#
# Duration -- parse/format human-readable durations, eg. 1w2d3h4m5.678s
#
class Duration( datetime.timedelta ):
    """The definition of a year is imprecise; we choose compatibility w/ the simplest 365.25 days/yr.
    An actual year is about 365.242196 days =~= 31,556,925.7344 seconds.  The official "leap year"
    calculation yields (365 + 1/4 - 1/100 + 1/400) * 86,400 == 31,556,952 seconds/yr.  We're
    typically dealing with human-scale time periods with this data structure, so use the simpler
    definition of a year, to avoid seemingly-random remainders when years are involved.

    Is a dateetime.timedelta, so works well with built-in datetime +/- timedelta functionality.

    """
    YR 				= 31557600
    WK				=   604800
    DY				=    86400
    HR				=     3600
    MN				=       60

    @classmethod
    def _format( cls, delta ):
        seconds			= delta.days * cls.DY + delta.seconds
        microseconds		= delta.microseconds
        result			= ''

        years			= seconds // cls.YR
        if years:
            result             += "{years}y".format( years=years )
        y_secs			= seconds % cls.YR

        weeks			= y_secs // cls.WK
        if weeks:
            result             += "{weeks}w".format( weeks=weeks )
        w_secs			= y_secs % cls.WK

        days			= w_secs // cls.DY
        if days:
            result             += "{days}d".format( days=days )
        d_secs			= w_secs % cls.DY

        hours			= d_secs // cls.HR
        if hours:
            result             += "{hours}h".format( hours=hours )
        h_secs			= d_secs % cls.HR

        minutes			= h_secs // cls.MN
        if minutes:
            result             += "{minutes}m".format( minutes=minutes )

        s			= h_secs % cls.MN
        is_us			= microseconds  % 1000 > 0
        is_ms			= microseconds // 1000 > 0
        if is_ms and ( s > 0 or is_us ):
            # s+us or both ms and us resolution; default to fractional
            result	       += "{s}.{us:0>6}".format( us=microseconds, s=s ).rstrip( '0' ) + 's'
        elif microseconds > 0 or s > 0:
            # s or sub-seconds remain; auto-scale to s/ms/us; the finest precision w/ data.
            if s:
                result         += "{s}s".format( s=s )
            if is_us:
                result         += "{us}us".format( us=microseconds )
            elif is_ms:
                result         += "{ms}ms".format( ms=microseconds // 1000 )
        elif microseconds == 0 and seconds == 0:
            # A zero duration
            result	       += "0s"
        else:
            # A non-empty duration w/ no remaining seconds output above; nothing left to do
            pass
        return result

    DURSPEC_RE			= re.compile(
        flags=re.IGNORECASE | re.VERBOSE,
        pattern=r"""
            ^
            (?:\s*(?P<y>\d+)\s*y((((ea)?r)s?)?)?)? # y|yr|yrs|year|years
            (?:\s*(?P<w>\d+)\s*w((((ee)?k)s?)?)?)?
            (?:\s*(?P<d>\d+)\s*d((((a )?y)s?)?)?)?
            (?:\s*(?P<h>\d+)\s*h((((ou)?r)s?)?)?)?
            (?:\s*(?P<m>\d+)\s*m((in(ute)?)s?)?)?  # m|min|minute|mins|minutes
            (?:
              (?:\s* # seconds mantissa (optional) + fraction (required)
                (?P<s_man>\d+)?
                [.,](?P<s_fra>\d+)\s*             s((ec(ond)?)s?)?
              )?
            | (?:
                (?:\s*(?P<s> \d+)\s*              s((ec(ond)?)s?)?)?
                (?:\s*(?P<ms>\d+)\s*(m|(milli))   s((ec(ond)?)s?)?)?
                (?:\s*(?P<us>\d+)\s*(u|μ|(micro)) s((ec(ond)?)s?)?)?
                (?:\s*(?P<ns>\d+)\s*(n|(nano))    s((ec(ond)?)s?)?)?
              )
            )
            \s*
            $
        """ )

    @classmethod
    def _parse( cls, durspec ):
        """Parses a duration specifier, returning the matching timedelta"""
        durmatch		= cls.DURSPEC_RE.match( durspec )
        if not durmatch:
            raise RuntimeError("Invalid duration specification: {durspec}".format( durspec=durspec ))
        seconds			= (
            int( durmatch.group( 's' ) or durmatch.group( 's_man' ) or 0 )
            + cls.MN * int( durmatch.group( 'm' ) or '0' )
            + cls.HR * int( durmatch.group( 'h' ) or '0' )
            + cls.DY * int( durmatch.group( 'd' ) or '0' )
            + cls.WK * int( durmatch.group( 'w' ) or '0' )
            + cls.YR * int( durmatch.group( 'y' ) or '0' )
        )
        microseconds		= (
            int( "{:0<6}".format( durmatch.group( 's_fra' ) or '0' ))
            + int( durmatch.group( 'ms' ) or '0' )  * 1000
            + int( durmatch.group( 'us' ) or '0' )
            + int( durmatch.group( 'ns' ) or '0' ) // 1000
        )
        return datetime.timedelta( seconds=seconds, microseconds=microseconds )

    def __new__( cls, value = None ):
        """Construct a Duration from something convertible into a datetime.timedelta.

        """
        if isinstance( value, type_str_base ):
            value		= cls._parse( value )
        if isinstance( value, (int,float) ):
            value		= datetime.timedelta( seconds=value )
        assert isinstance( value, datetime.timedelta ), \
            "Cannot construct a Duration from a {value!r}".format( value=value )
        # The value is (now) a datetime.timedelta; copy it's internals.
        self			= datetime.timedelta.__new__(
            cls,
            days	= value.days,
            seconds	= value.seconds,
            microseconds= value.microseconds
        )
        # self._days		= value.days
        # self._seconds		= value.seconds
        # self._microseconds	= value.microseconds
        # self._hashcode		= -1
        return self

    def __str__( self ):
        return self._format( self )

    def __float__( self ):
        return self.total_seconds()

    def __int__( self ):
        return int( self.total_seconds() )


def parse_seconds( seconds ):
    """Convert an <int>, <float>, "<float>", "[HHH]:MM[:SS[.sss]]", "1m30s" or a Duration to a float number of seconds.

    """
    if isinstance( seconds, datetime.timedelta ):	# <timedelta>, <Duration>
        return seconds.total_seconds()
    try:						# '1.23'
        return float( seconds )
    except ValueError:
        pass
    try:						# 'HHH:MM[:SS[.sss]]'
        return math.fsum(
            map(
                lambda p: p[0] * p[1],
                zip(
                    [ 60*60, 60, 1 ],
                    map(
                        lambda i: float( i or 0 ),
                        parse_seconds.HHMMSS_RE.search( seconds ).groups()
                    )
                )
            )
        )
    except Exception:					# '1m30s'
        pass
    return Duration( seconds ).total_seconds()
parse_seconds.HHMMSS_PAT	= r'(\d*):(\d{2})(?::(\d{2}(?:\.\d+)?))?'  # noqa: E305
parse_seconds.HHMMSS_RE		= re.compile(
    flags=re.IGNORECASE | re.VERBOSE, pattern=parse_seconds.HHMMSS_PAT )


#
# Some simpler datetime and duration handling functionality.
#
# NOTE: Does *not* support the ambiguous timezone abbreviations! (eg. MST/MDT instead of Canada/Mountain)
#
def parse_datetime( time, zone=None ):
    """Interpret the time string "2019/01/20 10:00" as a naive local time, in the specified time zone,
    eg. "Canada/Mountain" (default: "UTC").  Returns the datetime; default time zone: UTC.  If a
    timezone name follows the datetime, use it instead of zone/'UTC'.

    """
    tz			= pytz.timezone( zone or 'UTC' )
    # First, see if we can split out datetime and a specific timezone.  If not, just try
    # patterns against the supplied time string, unmodified, and default tz to zone/UTC.
    dtzmatch		= parse_datetime.DATETIME_RE.match( time )
    if dtzmatch:
        time		= dtzmatch.group( 'dt' )
        zone		= dtzmatch.group( 'tz' )
        if zone:
            tz		= pytz.timezone( str( zone ))

    # Then, try parsing some time formats w/ timezone data, and convert to the designated timezone
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S%z",
    ]:
        try:
            return datetime.datetime.strptime( time, fmt ).astimezone( tz )
        except Exception:
            pass

    # Next, try parsing some naive datetimes, and then localize them to their designated timezone
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]:
        try:
            return tz.localize( datetime.datetime.strptime( time, fmt ))
        except Exception:
            pass
    raise RuntimeError("Couldn't parse datetime from {time!r} w/ time zone {tz!r}".format(
        time=time, tz=tz ))
parse_datetime.DATETIME_PAT	= r"""
        # YYYY-MM-DDTHH:MM:SS.sss+ZZ:ZZ
        (?P<dt>[0-9-]+([ T][0-9:\.\+\-]+)?)
        # Optionally, whitespace followed by a Blah[/Blah] Timezone name, eg. Canada/Mountain
        (?:\s+
          (?P<tz>[a-z_-]+(/[a-z_-]*)*)
        )?
    """							# noqa: E305
parse_datetime.DATETIME_RE	= re.compile(
    flags	= re.IGNORECASE | re.VERBOSE,
    pattern	= r"""
        ^
        \s*
        {pattern}
        \s*
        $
    """.format( pattern=parse_datetime.DATETIME_PAT ))


#
# Config file handling
#
# Define the default paths used for configuration files, etc.
CONFIG_BASE			= 'crypto-licensing'
CONFIG_FILE			= CONFIG_BASE+'.cfg'    # Default application configuration file


class Timestamp( datetime.datetime ):
    """A simple Timestamp that can be specified from a Timestamp or datetime.datetime, and is always local to a
    specific timezone, and formats simply and deterministically.

    """
    UTC				= pytz.UTC
    LOC				= get_localzone()       # from environment TZ, /etc/timezone, etc.

    _precision			= 3			# How many default sub-second digits
    _epsilon			= 10**-_precision       # How small a difference to consider ==
    _fmt			= '%Y-%m-%d %H:%M:%S'	# 2014-04-01 10:11:12

    def __str__( self ):
        return self.render()

    def __repr__( self ):
        return '<%s =~= %.6f>' % ( self, self.timestamp() )

    def __new__( cls, *args, **kwds ):
        """Since datetime.datetime is immutable, we must use __new__ and return one."""
        kargs			= dict( zip( ('year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond', 'tzinfo' ), args ))
        assert len( kargs ) == len( args ), \
            "Too many args provided"
        kdup			= set( kargs ).intersection( kwds )
        assert not kdup, \
            "Duplicate positional and keyword args provided: {kdup!r}".format( kdup=kdup )
        kwds.update( kargs )

        # A Timestamp is *always* specific to a timezone; default is UTC.
        if kwds.get( 'tzinfo' ) is None:
            kwds['tzinfo']	= cls.UTC
        if set( kwds ) == set( 'tzinfo' ):
            # From current time
            kwds['year']	= timer()
        if set( kwds ) == {'year', 'tzinfo'} and isinstance( kwds['year'], (int,float) ):
            # From a single numeric timestamp
            kwds['year']	= datetime.datetime.fromtimestamp( kwds['year'], tz=kwds['tzinfo'] )
        if set( kwds ) == {'year', 'tzinfo'} and isinstance( kwds['year'], datetime.datetime ):
            # From a datetime.datetime, possibly converted into another timezone.
            dt			= kwds.pop( 'year' ).astimezone( kwds['tzinfo'] )
            kwds['year']	= dt.year
            kwds['month']	= dt.month
            kwds['day']		= dt.day
            kwds['hour']	= dt.hour
            kwds['minute']	= dt.minute
            kwds['second']	= dt.second
            kwds['microsecond']	= dt.microsecond
        # Finally, from a partial/complete date/time specification
        assert set( kwds ).issuperset( {'year', 'month', 'day'} ), \
            "Timestamp must specify at least y/m/d"
        return datetime.datetime.__new__( cls, **kwds )

    def render( self, tzinfo=None, ms=True, tzdetail=None ):
        """Render the time in the specified zone (default: local), optionally with milliseconds (default:
        True).

        If the resultant timezone is not UTC, include the timezone full name in the output by
        default.  Thus, the output is always deterministic (only UTC times may every be output
        without timezone information).

        If tzdetail is supplied, if bool/str and Truthy, always include full timezone name;
        if Falsey, include abbreviation (warning: NOT parsable, because abbreviations are
        non-deterministic!).  If int and Truthy, always include full numeric timezone offset; if
        Falsey; only with non-UTC timezones.

        """
        subsecond		= self._precision if ms is True else int( ms ) if ms else 0
        assert 0 <= subsecond <= 6, \
            "Invalid sub-second precision; must be 0-6 digits"
        value			= round( self.timestamp(), subsecond ) if subsecond else self.timestamp()
        tz			= tzinfo or self.LOC    # default to local timezone
        dt			= super( Timestamp, self ).astimezone( tz )
        result			= dt.strftime( self._fmt )
        if subsecond:
            result	       += ( '%.*f' % ( subsecond, value ))[-subsecond-1:]
        if tz is not self.UTC or tzdetail is not None:
            if isinstance( tzdetail, (bool, type_str_base, type(None)) ):
                if tzdetail is None or bool( tzdetail ):
                    result       += " " + dt.tzinfo.zone  # full zone name if tzdetail is bool/str and Truthy (default)
                else:
                    # Warning: result not parse-able, b/c TZ abbreviations are wildly non-deterministic
                    result       += dt.strftime(' %Z' )   # default abbreviation for non-UTC (only if tzdetail=='')
            elif isinstance( tzdetail, (int, float) ):
                if bool( tzdetail ):
                    result       += dt.strftime( '%z' )   # otherwise, append numeric tz offset (only if tzdetail==1)

        return result

    def __float__( self ):
        return self.timestamp()

    def __int__( self ):
        return int( self.timestamp() )

    def timestamp( self ):
        """Exists in Python 3.3+.  Convert a timezone-aware datetime to a UNIX timestamp.  You'd think
        strftime( "%s.%f" )?  You'd be wrong; a timezone-aware datetime should always strftime
        to the same (correct) UNIX timestamp via its "%s" format, but this also doesn't work.

        Convert the time to a UTC time tuple, then use calendar.timegm to take a UTC time tuple and
        compute the UNIX timestamp.

        """
        try:
            return super( Timestamp, self ).timestamp()
        except AttributeError:
            return calendar.timegm( self.utctimetuple() ) + self.microsecond / 1000000

    # Comparisons.  Always equivalent to lexicographically, in UTC to 3 decimal places.  However,
    # we'll compare numerically, to avoid having to render/compare strings; if the <self>.value is
    # within _epsilon (default: 0.001) of <rhs>.value, it is considered equal.
    def __lt__( self, rhs ):
        assert isinstance( rhs, Timestamp )
        return self.timestamp() + self.__class__._epsilon < rhs.timestamp()

    def __gt__( self, rhs ):
        assert isinstance( rhs, Timestamp )
        return self.timestamp() - self.__class__._epsilon > rhs.timestamp()

    def __le__( self, rhs ):
        return not self.__gt__( rhs )

    def __ge__( self, rhs ):
        return not self.__lt__( rhs )

    def __eq__( self, rhs ):
        return not self.__ne__( rhs )

    def __ne__( self, rhs ):
        return self.__lt__( rhs ) or self.__gt__( rhs )

    # Add/subtract Duration or numeric seconds.  +/- 0 is a noop/copy.  A Timestamp /
    # datetime.datetime is immutable, so cannot implemente __i{add/sub}__.  Converts to timedelta,
    # and uses underlying __{add,sub}__.
    def __add__( self, rhs ):
        """Convert any int/float/str, etc. to a Duration/timedelta, and add it to the current Timestamp,
        retaining its timezone preference.

        """
        if not isinstance( rhs, Duration):
            rhs		= Duration( rhs )
        if rhs.total_seconds():
            return Timestamp( super( Timestamp, self ).__add__( rhs ), tzinfo=self.tzinfo )
        return self


    def __sub__( self, rhs ):
        """Convert any int/float/str, etc. to a Duration/timedelta, and subtract it from the current
        Timestamp, retaining its timezone preference.  If another Timestamp/datetime.datetime is
        supplied, return the difference as a Duration instead.

        """
        if isinstance( rhs, datetime.datetime ):
            # Subtracting datetimes; result is a Duration; obtain from existing __sub__ returning a timedelta
            return Duration( super( Timestamp, self ).__sub__( rhs ))
        # Subtracting something else; must be convertible by Duration into a timedelta
        rhs		= Duration( rhs )
        if rhs.total_seconds():
            return Timestamp( super( Timestamp, self ).__sub__( rhs ), tzinfo=self.tzinfo )
        return self


Timespan = collections.namedtuple( 'Timespan', ('start', 'length') )


def config_paths( filename, extra=None ):
    """Yield the configuration search paths in *reverse* order of precedence (furthest or most
    general, to nearest or most specific).

    This is the order that is required by configparser; settings configured in "later" files
    override those in "earlier" ones.

    For other purposes (eg. loading complete files), the order is likely reversed!  The caller must
    do this manually.

    """
    yield os.path.join( os.path.dirname( __file__ ), filename )			# installation root dir
    yield os.path.join( os.getenv( 'APPDATA', os.sep + 'etc' ), filename )      # global app data dir, eg. /etc/
    yield os.path.join( os.path.expanduser( '~' ), '.'+CONFIG_BASE, filename )  # user dir, ~username/.crypto-licensing/name
    yield os.path.join( os.path.expanduser( '~' ), '.' + filename )		# user dir, ~username/.name
    for e in extra or []:							# any extra dirs...
        yield os.path.join( e, filename )
    yield filename								# current dir (most specific)


# Default configuration files path, In 'configparser' expected order (most general to most specific)
config_files			= list( config_paths( CONFIG_FILE ))

try:
    ConfigNotFoundError		= FileNotFoundError
except NameError:
    ConfigNotFoundError		= IOError		# Python2 compatibility


def config_open( name, mode=None, extra=None, skip=None, reverse=True, **kwds ):
    """Find and open all glob-matched file name(s) found on the standard or provided configuration file
    paths (plus any extra), in most general to most specific order.  Yield the open file(s), or
    raise a ConfigNotFoundError (a FileNotFoundError or IOError in Python3/2 if no matching file(s)
    at all were found, to be somewhat consistent with a raw open() call).

    We traverse these in reverse order by default: nearest and most specific, to furthest and most
    general, and any matching file(s) in ascending sorted order; specify reverse=False to obtain the
    files in the most general/distant configuration first.

    By default, we assume the matching target file(s) are UTF-8/ASCII text files, and default to
    open in 'r' mode.

    A 'skip' glob pattern or predicate function taking a single name and returning True/False may be
    supplied.

    """
    if isinstance( skip, type_str_base ):
        filtered		= lambda names: (n for n in names if not fnmatch.fnmatch( n, skip ))  # noqa: E731
    elif hasattr( skip, '__call__' ):
        filtered		= lambda names: (n for n in names if not skip( n ))  # noqa: E731
    elif skip is None:
        filtered		= lambda names: names  # noqa: E731
    else:
        raise AssertionError( "Invalid skip={!r} provided".format( skip ))

    search			= list( config_paths( name, extra=extra ))
    if reverse:
        search			= reversed( search )
    for fn in search:
        for gn in sorted( filtered( glob.glob( fn ))):
            try:
                yield open( gn, mode=mode or 'r', **kwds )
            except Exception:
                # The file couldn't be opened (eg. permissions)
                pass


def deduce_name( basename=None, extension=None, filename=None, package=None ):
    assert basename or ( filename or package ), \
        "Cannot deduce basename without either filename (__file__) or package (__package__)"
    if basename is None:
        if filename:
            basename		= os.path.basename( filename )      # eg. '/a/b/c/d.py' --> 'd.py'
            if '.' in basename:
                basename	= basename[:basename.rfind( '.' )]  # up to last '.'
        else:
            basename		= package
            if '.' in basename:
                basename	= basename[:basename.find( '.' )]   # up to first '.'
    name			= basename
    if extension and '.' not in name:
        if extension[0] != '.':
            name	       += '.'
        name		       += extension
    return name


def config_open_deduced( basename=None, mode=None, extension=None, filename=None, package=None, **kwds ):
    """Find any glob-matched configuration file(s), optionally deducing the basename from the provided
    __file__ filename or __package__ package name, returning the open file or raising a ConfigNotFoundError
    (or FileNotFoundError, or IOError in Python2).

    """
    for f in config_open(
            name=deduce_name(
                basename=basename, extension=extension, filename=filename, package=package ),
            mode=mode or 'r', **kwds ):
        yield f
