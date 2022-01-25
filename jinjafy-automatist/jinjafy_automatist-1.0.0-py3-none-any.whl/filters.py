#import iso8601
import datetime


# def parsedate (x):
#     if type(x) == datetime.datetime:
#         return x
#     try:
#         return iso8601.parse_date(x)
#     except iso8601.ParseError:
#         return datetime.datetime.fromtimestamp(int(x))

def datetimeformat (t, format='%Y-%m-%d %H:%M:%S'):
    return parsedate(t).strftime(format)

# def datetimeformat (t, format='%Y-%m-%d %H:%M:%S'):
#     return time.strftime(format, time.localtime(t))

# from itertools import izip_longest

# def grouper(iterable, n, fillvalue=None):
#     "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
#     args = [iter(iterable)] * n
#     return zip_longest(fillvalue=fillvalue, *args)

def humanize_bytes(bytesize, precision=2):
    """
    Humanize byte size figures
    """
    abbrevs = (
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'bytes')
    )
    if bytesize == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytesize >= factor:
            break
    if factor == 1:
        precision = 0
    return '%.*f %s' % (precision, bytesize / float(factor), suffix)

import math

def timecode(rawsecs, fract=True, alwaysfract=True, fractdelim='.', alwayshours=True):
    # returns a string in HH:MM:SS[.xxx] notation
    # if fract is True, uses .xxx if either necessary (non-zero)
    # OR alwaysfract is True
    hours = math.floor(rawsecs / 3600)
    rawsecs -= hours * 3600
    mins = math.floor(rawsecs / 60)
    rawsecs -= mins * 60
    if fract:
        secs = math.floor(rawsecs)
        rawsecs -= secs
        if (rawsecs > 0 or alwaysfract):
            fract = "%.03f" % rawsecs
            if hours or alwayshours:
                return "%02d:%02d:%02d%s%s" % (hours, mins, secs, fractdelim, \
                        fract[2:])
            else:
                return "%02d:%02d%s%s" % (mins, secs, fractdelim, fract[2:])
        else:
            if hours or alwayshours:
                return "%02d:%02d:%02d" % (hours, mins, secs)
            else:
                return "%02d:%02d" % (mins, secs)

    else:
        secs = round(rawsecs)
        if hours or alwayshours:
            return "%02d:%02d:%02d" % (hours, mins, secs)
        else:
            return "%02d:%02d" % (mins, secs)

all = {
    'datetimeformat': datetimeformat,
    'timecode': timecode,
    'humanize_bytes': humanize_bytes
}
