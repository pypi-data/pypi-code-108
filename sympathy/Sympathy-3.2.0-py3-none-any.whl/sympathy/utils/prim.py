# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Module for primitive, but useful, operations on files, lists and dictionaries.
"""
from collections import OrderedDict
from itertools import islice
from contextlib import contextmanager
import re
import os
import sys
import json
import datetime
import urllib
import urllib.request
import urllib.parse


def is_windows():
    """Return True if Sympathy is running on Windows."""
    return sys.platform == 'win32'


def is_linux():
    """Return True if Sympathy is running on Linux."""
    return sys.platform.startswith('linux')


def is_osx():
    """Return True if Sympathy is running on OS/X."""
    return sys.platform == 'darwin'


def is_cygwin():
    """Return True if Sympathy is running on Cygwin."""
    return sys.platform == 'cygwin'


def is_posix():
    """Return True if Sympathy is running on a posix System."""
    return os.name == 'posix'


def get_home_dir():
    """
    Return user's home directory or, if that can't be found, the current
    directory.
    """
    home_dir = os.path.expanduser(u'~')

    # os.path.expanduser can fail, for example on Windows if HOME or
    # USERPROFILE don't exist in the environment. If it fails it returns the
    # path unchanged.
    if home_dir == u'~':
        return os.getcwd()
    else:
        return home_dir


def containing_dirs(paths):
    """
    Filter contained paths leaving only the ones that are not contained in a
    subdirectory of any other path.
    Returns filtered paths.

    >>> paths = ['/usr/bin', '/usr', '/usr/local', '/opt', '/opt/local']
    >>> get_containing_dirs(paths)
    ['/usr', '/opt']
    """
    normal = [os.path.normcase(os.path.realpath(path)).rstrip(os.path.sep)
              for path in paths]
    unique = OrderedDict.fromkeys(normal).keys()
    return [path for path in unique
            if not any(path.startswith(other)
                       for other in unique if other != path)]


def resolve_relative_path(path):
    relative_path = ''
    if path:
        try:
            relative_path = os.path.relpath(str(path))
        except Exception:
            relative_path = os.path.abspath(str(path))
    return relative_path


@contextmanager
def open_url(url, mode=None):
    open_file = None
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == 'file' or parsed.scheme == '':
        url = uri_to_path(url)
        opener = lambda url, mode: open(url, mode=mode)
    else:
        opener = lambda url, mode: urllib.request.urlopen(url)
    try:
        open_file = opener(url, mode)
        yield open_file
    finally:
        if open_file is not None:
            open_file.close()


def dottedpath(path):
    return path.replace(os.path.sep, '.').replace(':.', '.')


def uri_to_path(url):
    """
    Return a local file or UNC path from a file:-URI.

    The result depends on the host OS.

    On Windows:
    uri_to_path('file:///C:/Users') => 'C:\\Users'

    On Unix:
    uri_to_path('file:///home') => '/home'
    """
    if isinstance(url, str):
        url = url.encode('ascii')
    parsed = urllib.parse.urlparse(url)
    path = parsed.path

    if not isinstance(path, str):
        path = path.decode('ascii')

    netloc = parsed.netloc
    local_path = urllib.request.url2pathname(path)

    if netloc:
        if isinstance(netloc, bytes):
            netloc = netloc.decode('ascii')

        local_path = '//{}{}'.format(netloc, local_path)

    return os.path.sep.join(local_path.split('/'))


def localuri(path):
    """Create absolute uri from absolute local path."""
    try:
        encoded_path = urllib.request.pathname2url(
            path.encode('utf8'))
    except TypeError:
        encoded_path = urllib.request.pathname2url(path)
    return urllib.parse.urljoin('file:', encoded_path)


def unipath(path):
    """
    Returns universal path for usage in URL, changing all native file
    separators to forward slashes (``'/'``).
    >>> unipath('/usr/bin')
    '/usr/bin'

    However:
    unipath('C:\\Users') should evaluate to C:/Users, on windows and other
    systems where \\ is a separator.
    """
    return '/'.join(path.split(os.sep))


def unipath_separators(path):
    return '/'.join(path.split('\\'))


def nativepath_separators(path):
    return path.replace('\\', os.path.sep).replace('/', os.path.sep)


def nativepath(path):
    """
    Returns a native path from an URL, changing all forward slashes to native
    file separators.
    """
    return os.path.normpath(path)


def concat(nestedlist):
    """
    Concatenate one level of list nesting.
    Returns a new list with one level less of nesting.
    """
    return [item for sublist in nestedlist for item in sublist]


def flip(nested):
    """
    Flips a double nested dict so that the inner dict becomes the outer one.
    Returns a new flipped dictionary.
    """
    result = {}
    for key1, value1 in nested.items():
        for key2, value2 in value1.items() if value1 else {}:
            result[key2] = result.get(key2, {})
            result[key2][key1] = value2
    return result


def group_pairs(pair_list):
    """Return new list of key-value pairs grouped by key."""
    result = OrderedDict()
    for key, value in pair_list:
        acc = result.setdefault(key, [])
        acc.append(value)
    return result.items()


def ungroup_pairs(pair_list):
    """Return new ungrouped list of key-value pairs."""
    return [(key, value) for key, values in pair_list for value in values]


def fuzzy_filter(pattern, items):
    """Filter items whose keys do not match pattern."""
    def fix(char):
        special = """'"*^-.?${},+[]()"""
        if char in special:
            return '\\' + char
        else:
            return char

    escaped = [fix(char) for char in pattern]
    pattern = re.compile('.*'.join([''] + escaped + ['']), re.IGNORECASE)
    return [(key, value) for key, value in items
            if pattern.match(key)]


def nth(iterable, n, default=None):
    """Returns the nth item or a default value."""
    return next(islice(iterable, n, None), default)


def encode_basic(basic, encoding='utf-8'):
    """
    Encode basic structure consisting of basic python types, such as the
    result of using json.load so that all str strings are encoded.
    Dictionary keys included.
    Return new encoded structure.
    """
    if isinstance(basic, dict):
        return {encode_basic(key, encoding): encode_basic(value, encoding)
                for key, value in basic.items()}
    elif isinstance(basic, list):
        return [encode_basic(value, encoding) for value in basic]
    elif isinstance(basic, str):
        return basic.encode(encoding)
    else:
        return basic


def memoize(function):
    """Memoization of function with non-keyword arguments."""
    memoized = {}

    def wrapper(*args):
        if args not in memoized:
            result = function(*args)
            memoized[args] = result
            return result
        return memoized[args]
    wrapped_function = wrapper
    wrapped_function.__name__ = wrapper.__name__
    wrapped_function.__doc__ = wrapper.__doc__
    return wrapped_function


def combined_key(string):
    """
    Alphanumeric key function.
    It computes the sorting key from string using the string and integer parts
    separately.
    """
    def to_int(string):
        try:
            return int(string)
        except ValueError:
            return string
    return [to_int(part) for part in re.split('([0-9]+)', string)]


def absolute_paths(root, paths):
    return [os.path.normpath(
        path if os.path.isabs(path)
        else os.path.join(root, path)) for path in paths]


def import_statements(filenames):
    """Return a list of all import statements in filenames."""
    regex = re.compile(
        br'^((?:import .*|from [^\.][^\n]* import (?:\([^\)]+\)|.*)?))',
        re.MULTILINE)
    result = []

    for filename in filenames:
        try:
            with open(filename, 'rb') as f:
                result.extend(regex.findall(f.read()))
        except Exception:
            pass

    return sorted(set(
        re.sub(b'[ ]+', b' ',
               re.sub(b'[\n\r()]', b' ', i)).rstrip().decode('ascii')
        for i in set(result)))


def limit_traceback(full_traceback, filename=None):
    """
    Take a full traceback in the format returned by traceback.format_exception
    and return a string produced by joining the lines.

    If filename is specified then traceback rows that are found before the
    first line containing filename will be dropped.
    """
    if filename is None:
        return ''.join(full_traceback)

    filename = os.path.basename(filename)
    start = 1

    for i, row in enumerate(full_traceback):
        if filename in row:
            start = i
            break

    return ''.join([full_traceback[0]] + full_traceback[start:])


def sympathy_path():
    """Return the path to the sympathy package."""
    file_ = __file__
    path = os.path.dirname(file_)
    return os.path.abspath(os.path.join(path, '..'))


def sylib_path():
    """Return the path to the sylib package."""
    file_ = __file__
    path = os.path.dirname(file_)
    return os.path.abspath(os.path.join(path, '..', '..', 'sylib'))


def resources_path():
    """Return the path to the Resource folder."""
    return os.path.join(sympathy_path(), 'resources')


def config():
    """Return the contents of the config file."""
    with open(os.path.join(resources_path(), 'config.json')) as f:
        return json.load(f)


def icons_path():
    """Return the path to the icons folder."""
    return os.path.join(resources_path(), 'icons')


def fonts_path():
    """Return the path to the fonts folder."""
    return os.path.join(resources_path(), 'fonts')


def test_path(package='sympathy'):
    return os.path.abspath(
        os.path.join(sympathy_path(), '..', package, 'test'))


def examples_path(package='sympathy'):
    return os.path.abspath(
        os.path.join(sympathy_path(), '..', package, 'examples'))


def misc_path(package='sympathy'):
    return os.path.abspath(
        os.path.join(sympathy_path(), '..', '..', 'misc', package))


def doc_path(package='sympathy', package_path=None):
    if package_path is None:
        package_path = sympathy_path()
    return os.path.abspath(
        os.path.join(package_path, '..', '..', 'doc', package))


def get_icon_path(name):
    """Return the absolute path for the icon with name `name`."""
    return os.path.join(icons_path(), name)


def format_display_string(string: str, length: int = 0) -> str:
    """
    Removes newlines and other whitespace and replaces them with a single
    space. Also removes whitespace at the beginning and the end of the string.
    If length is not zero the returned string will be truncated to that length.
    """
    new_string = re.sub(r'\s+', ' ', string, flags=re.UNICODE).strip()
    return new_string if length == 0 else new_string[:length]


def parse_isoformat_datetime(value):
    """
    Return naive datetime parsed from isoformat string.
    """
    try:
        value = datetime.datetime.strptime(
            value, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        value = datetime.datetime.strptime(
            value, "%Y-%m-%dT%H:%M:%S")
    return value


def samefile(filename0, filename1):
    try:
        res = os.path.samefile(filename0, filename1)
    except (OSError, IOError):
        res = False
    return res


def chunk(sequence, length):
    len_sequence = len(sequence)
    for i in range(0, len_sequence, length):
        yield sequence[i: i + length]


def rechunk(chunks, length, join):
    size = 0
    buf = []

    for chunk in chunks:
        size += len(chunk)

        while size >= length:
            diff = length - size % length
            buf.append(chunk[:diff])
            yield join(buf)
            buf.clear()
            chunk = chunk[diff:]
            size = len(chunk)

        if chunk:
            buf.append(chunk)

    if buf:
        yield join(buf)
