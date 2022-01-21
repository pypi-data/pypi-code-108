# -*- coding: utf-8 -*-
#
# vim: expandtab shiftwidth=4 softtabstop=4
#
"""ownCloud util module

"""
from __future__ import absolute_import, print_function, division

import locale

import pytz
import datetime
import os
import tempfile
from logging import debug, warning, error
from hashlib import md5

from tzlocal import get_localzone

try:
    unicode
except NameError:
    # python 3 support
    # In python 3, unicode -> str, and str -> bytes
    unicode = str


def hash_file_md5(filename):
    h = md5()
    with open(deunicodise(filename), "rb") as fp:
        while True:
            # Hash 32kB chunks
            data = fp.read(32*1024)
            if not data:
                break
            h.update(data)
    return h.hexdigest()

import six


def timedelta_to_seconds(delta):
    '''Convert a timedelta to seconds with the microseconds as fraction
    Note that this method has become largely obsolete with the
    `timedelta.total_seconds()` method introduced in Python 2.7.
    '''
    # Only convert to float if needed
    if delta.microseconds:
        total = delta.microseconds * 1e-6
    else:
        total = 0
    total += delta.seconds
    total += delta.days * 60 * 60 * 24
    return total

def format_oc_last_modified_time(time_str):
    gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
    date = datetime.datetime.strptime(time_str, gmt_format).replace(tzinfo=pytz.utc)
    return date.astimezone(get_localzone()).strftime("%Y-%m-%d %H:%M:%S")


def format_time(timestamp, precision=datetime.timedelta(seconds=1)):
    '''Formats timedelta/datetime/seconds
    '''
    precision_seconds = precision.total_seconds()

    if isinstance(timestamp, six.string_types + six.integer_types + (float,)):
        try:
            castfunc = six.integer_types[-1]
            timestamp = datetime.timedelta(seconds=castfunc(timestamp))
        except OverflowError:  # pragma: no cover
            timestamp = None

    if isinstance(timestamp, datetime.timedelta):
        seconds = timestamp.total_seconds()
        # Truncate the number to the given precision
        seconds = seconds - (seconds % precision_seconds)

        return str(datetime.timedelta(seconds=seconds))
    elif isinstance(timestamp, datetime.datetime):  # pragma: no cover
        # Python 2 doesn't have the timestamp method
        if hasattr(timestamp, 'timestamp'):
            seconds = timestamp.timestamp()
        else:
            seconds = timedelta_to_seconds(timestamp - epoch)

        # Truncate the number to the given precision
        seconds = seconds - (seconds % precision_seconds)

        try:  # pragma: no cover
            if six.PY3:
                dt = datetime.datetime.fromtimestamp(seconds)
            else:
                dt = datetime.datetime.utcfromtimestamp(seconds)
        except ValueError:  # pragma: no cover
            dt = datetime.datetime.max
        return str(dt)
    elif isinstance(timestamp, datetime.date):
        return str(timestamp)
    elif timestamp is None:
        return '--:--:--'
    else:
        raise TypeError('Unknown type %s: %r' % (type(timestamp), timestamp))


def read_cache_file(cache_file_name, cache_validity = datetime.timedelta(hours=8)):
    file_path = os.path.join(tempfile.gettempdir(), cache_file_name)
    if not os.path.exists(file_path):
        return None
    if datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime) + cache_validity < datetime.datetime.now():
        delete_cache_file(cache_file_name)
        return None
    with open(file_path, 'r') as fr:
        return fr.readline()


def write_cache_file(cache_file_name, data):
    file_path = os.path.join(tempfile.gettempdir(), cache_file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as fw:
        fw.write(data)


def delete_cache_file(cache_file_name):
    file_path = os.path.join(tempfile.gettempdir(), cache_file_name)
    if os.path.exists(file_path):
        os.remove(file_path)


def convert(string):
    if six.PY3:
        return unicodise_safe(deunicodise(string, 'UTF-8'))
    else:
        return string


def unicodise(string, encoding = None, errors = "replace", silent=False):
    """
    Convert 'string' to Unicode or raise an exception.
    """
    if not encoding:
        encoding = locale.getpreferredencoding() or "UTF-8"

    if type(string) == unicode:
        return string

    if not silent:
        debug("Unicodising %r using %s" % (string, encoding))
    try:
        return unicode(string, encoding, errors)
    except UnicodeDecodeError:
        raise UnicodeDecodeError("Conversion to unicode failed: %r" % string)


def unicodise_s(string, encoding = None, errors = "replace"):
    """
    Alias to silent version of unicodise
    """
    return unicodise(string, encoding, errors, True)


def deunicodise(string, encoding = None, errors = "replace", silent=False):
    """
    Convert unicode 'string' to <type str>, by default replacing
    all invalid characters with '?' or raise an exception.
    """

    if not encoding:
        encoding = locale.getpreferredencoding() or "UTF-8"

    if type(string) != unicode:
        return string

    if not silent:
        debug("DeUnicodising %r using %s" % (string, encoding))
    try:
        return string.encode(encoding, errors)
    except UnicodeEncodeError:
        raise UnicodeEncodeError("Conversion from unicode failed: %r" % string)


def deunicodise_s(string, encoding = None, errors = "replace"):
    """
    Alias to silent version of deunicodise
    """
    return deunicodise(string, encoding, errors, True)


def unicodise_safe(string, encoding = None):
    """
    Convert 'string' to Unicode according to current encoding
    and replace all invalid characters with '?'
    """

    return unicodise(deunicodise(string, encoding), encoding).replace(u'\ufffd', '?')


def format_size(size, human_readable = False, floating_point = False):
    size = floating_point and float(size) or int(size)
    if human_readable:
        coeffs = ['K', 'M', 'G', 'T']
        coeff = ""
        while size > 2048:
            size /= 1024
            coeff = coeffs.pop(0)
        return (floating_point and float(size) or int(size), coeff)
    else:
        return (size, "")


class UploadIterator(object):
    def __init__(self, stream, progress, size=None, buff_size=1 << 13):
        self.buff_size = buff_size
        self.stream = stream
        self.progress = progress
        self.size = size

    def __iter__(self):
        while True:
            data = self.stream.read(self.buff_size)
            if not data:
                break
            yield data
            self.progress.update(delta_position=len(data))

    def __len__(self):
        if self.size:
            return self.size
        return self.progress.total_size


class IterableToFileAdapter(object):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = len(iterable)

    def read(self, size=-1): # TBD: add buffer for `len(data) > size` case
        return next(self.iterator, b'')

    def __len__(self):
        return self.length


def normalize_oc_path(oc_path):
    if not oc_path.startswith('oc://'):
        raise ValueError("Owncloud path must start with oc://")
    path = oc_path[5:]
    if not path.startswith('/'):
        path = '/' + path
    return path


def format_oc_path_output(path):
    if not path.startswith('/'):
        path = '/' + path
    return 'oc:/' + path


if __name__ == '__main__':
    print("/".split('/'))
    print(os.listdir("/"))
    print(os.path.isfile("/a"))
    print(format_oc_last_modified_time("Sat, 10 Oct 2020 08:14:42 GMT"))