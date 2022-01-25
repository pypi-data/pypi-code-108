import click
import datetime
import logging
import os
import pathlib
import re
import subprocess
import sys
import threading
import typing
from dateutil.tz import tzoffset


class ExtendedLogger(logging.Logger):
    """
    Extend the logging.Logger class.
    """
    def __init__(self, name, level=logging.NOTSET) -> None:
        self._count = 0
        self._countLock = threading.Lock()
        return super(ExtendedLogger, self).__init__(name, level)

    def _build_message(self, msg: str, arrow: str=None, indent: int=0, bold: bool=False) -> str:
        """
        Apply format parameters to a raw string.
        """
        msg = re.sub(r'\s+', ' ', msg.strip())

        if bold:
            msg = click.style(msg, bold=True)

        arrow_str = click.style('==> ', fg=arrow, bold=True) if arrow is not None else ''
        indent_str = '  ' * indent

        msg = str(msg)
        return f'{indent_str} {arrow_str}{msg}'

    def info(self, msg: str, *args, **kwargs):
        """
        Override the logging.Logger.info() method.
        """
        formatted_msg = self._build_message(msg, *args, **kwargs)
        return super(ExtendedLogger, self).info(formatted_msg)

    def warning(self, msg: str, *args, **kwargs):
        """
        Override the logging.Logger.warning() method.
        """
        formatted_msg = self._build_message(msg, *args, **kwargs)
        return super(ExtendedLogger, self).warning(formatted_msg)

    def error(self, msg: str, *args, **kwargs):
        """
        Override the logging.Logger.error() method.
        """
        formatted_msg = self._build_message(msg, *args, **kwargs)
        return super(ExtendedLogger, self).error(formatted_msg)

    def critical(self, msg: str, *args, **kwargs):
        """
        Override the logging.Logger.critical() method.
        """
        formatted_msg = self._build_message(msg, *args, **kwargs)
        return super(ExtendedLogger, self).critical(formatted_msg)


def logger_setup(name: str=__name__, level: int=logging.DEBUG) -> logging.Logger:
    """
    Standardize logger setup.
    """
    logging.setLoggerClass(ExtendedLogger)
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')

    if logger.hasHandlers():
        logger.handlers.clear()

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.setLevel(level)
    return logger


logger = logger_setup(name='sql-query-tools.utils', level=logging.WARNING)


def assert_value_dtype(value: typing.Any, dtype: str, return_coerced_value: bool=False, stop: bool=False) -> bool:
    """
    Test if a value is an instance of type `dtype`. May accept a value of any kind.

    Parameter `dtype` must be one of ['bool', 'str', 'string', 'int', 'integer',
    'float', 'date', 'datetime', 'path', 'path exists'].

    Parameter `return_coerced_value` will cause this function to return `value` as type
    `dtype` if possible, and will raise an error otherwise.

    Parameter `stop` will cause this function to raise an error if `value` cannot be
    coerced to `dtype` instead of simply logging the error message.
    """
    class Attribute():
        """
        Empty class defined for convenient use.
        """
        pass

    def define_date_regex():
        """
        Define regex strings for all valid date components.
        """
        rgx = Attribute()
        rgx.sep = r'(\.|\/|-|_|\:)'

        rgx.year = r'(?P<year>\d{4})'
        rgx.month = r'(?P<month>\d{2})'
        rgx.day = r'(?P<day>\d{2})'

        rgx.hour = r'(?P<hour>\d{2})'
        rgx.minute = r'(?P<minute>\d{2})'
        rgx.second = r'(?P<second>\d{2})'
        rgx.microsecond = r'(?P<microsecond>\d+)'

        rgx.tz_sign = r'(?P<tz_sign>-|\+)'
        rgx.tz_hour = r'(?P<tz_hour>\d{1,2})'
        rgx.tz_minute = r'(?P<tz_minute>\d{1,2})'

        rgx.date = f'{rgx.year}{rgx.sep}{rgx.month}{rgx.sep}{rgx.day}'
        rgx.datetime = fr'{rgx.date} {rgx.hour}{rgx.sep}{rgx.minute}{rgx.sep}{rgx.second}'
        rgx.datetime_timezone = fr'{rgx.datetime}{rgx.tz_sign}{rgx.tz_hour}(:){rgx.tz_minute}'
        rgx.datetime_microsecond = fr'{rgx.datetime}(\.){rgx.microsecond}'

        return rgx

    def anchor(x):
        """
        Add regex start and end anchors to a string.
        """
        return '^' + x + '$'


    valid_dtypes = ['bool',
                    'str', 'string',
                    'int', 'integer',
                    'float',
                    'date',
                    'datetime',
                    'path',
                    'path exists']
    assert dtype in valid_dtypes, f"Datatype must be one of {', '.join(valid_dtypes)}"

    # Date/datetime regex definitions
    rgx = define_date_regex()

    coerced_value = None

    # Test bool
    if dtype == 'bool':
        if isinstance(value, bool):
            coerced_value = value
        else:
            if str(value).lower() in ['true', 't', 'yes', 'y']:
                coerced_value = True
            elif str(value).lower() in ['false', 'f', 'no', 'n']:
                coerced_value = False

    # Test string
    elif dtype in ['str', 'string']:
        try:
            coerced_value = str(value)
        except Exception as e:
            if stop:
                raise e
            else:
                logger.warning(str(e))

    # Test integer
    elif dtype in ['int', 'integer']:
        if isinstance(value, int):
            coerced_value = value
        elif str(value).isdigit():
            coerced_value = int(value)
        else:
            try:
                coerced_value = int(value)
            except Exception as e:
                if stop:
                    raise e
                else:
                    logger.warning(str(e))

    # Test float
    elif dtype == 'float':
        if isinstance(value, float) or isinstance(value, int):
            coerced_value = float(value)
        elif '.' in str(value):
            try:
                coerced_value = float(value)
            except Exception as e:
                if stop:
                    raise e
                else:
                    logger.warning(str(e))

    # Test date
    elif dtype == 'date':
        m = re.search(anchor(rgx.date), str(value).strip())
        if m:
            dt_components = dict(year=m.group('year'), month=m.group('month'), day=m.group('day'))
            dt_components = {k: int(v) for k, v in dt_components.items()}
            coerced_value = datetime.datetime(**dt_components)

    # Test datetime
    elif dtype == 'datetime':
        m_dt = re.search(anchor(rgx.datetime), str(value).strip())
        m_dt_tz = re.search(anchor(rgx.datetime_timezone), str(value).strip())
        m_dt_ms = re.search(anchor(rgx.datetime_microsecond), str(value).strip())

        if m_dt:
            dt_components = dict(year=m_dt.group('year'),
                                 month=m_dt.group('month'),
                                 day=m_dt.group('day'),
                                 hour=m_dt.group('hour'),
                                 minute=m_dt.group('minute'),
                                 second=m_dt.group('second'))
            dt_components = {k: int(v) for k, v in dt_components.items()}
            coerced_value = datetime.datetime(**dt_components)

        elif m_dt_tz:
            dt_components = dict(year=m_dt_tz.group('year'),
                                 month=m_dt_tz.group('month'),
                                 day=m_dt_tz.group('day'),
                                 hour=m_dt_tz.group('hour'),
                                 minute=m_dt_tz.group('minute'),
                                 second=m_dt_tz.group('second'))
            dt_components = {k: int(v) for k, v in dt_components.items()}

            second_offset = int(m_dt_tz.group('tz_hour')) * 60 * 60
            second_offset = -second_offset if m_dt_tz.group('tz_sign') == '-' else second_offset

            dt_components['tzinfo'] = tzoffset(None, second_offset)
            coerced_value = datetime.datetime(**dt_components)

        elif m_dt_ms:
            dt_components = dict(year=m_dt_ms.group('year'),
                                 month=m_dt_ms.group('month'),
                                 day=m_dt_ms.group('day'),
                                 hour=m_dt_ms.group('hour'),
                                 minute=m_dt_ms.group('minute'),
                                 second=m_dt_ms.group('second'),
                                 microsecond=m_dt_ms.group('microsecond'))
            dt_components = {k: int(v) for k, v in dt_components.items()}
            coerced_value = datetime.datetime(**dt_components)

    # Test path
    elif dtype == 'path':
        if '/' in value or value == '.':
            coerced_value = value

    # Test path exists
    elif dtype == 'path exists':
        if os.path.isfile(value) or os.path.isdir(value):
            coerced_value = value

    # Close function
    if coerced_value is None:
        debug_str = f"Unable to coerce value '{str(value)}' (dtype: {type(value).__name__}) to {dtype}"
        logger.debug(debug_str)

        if return_coerced_value:
            raise ValueError(debug_str)
        else:
            return False

    else:
        if return_coerced_value:
            return coerced_value
        else:
            return True


def listfiles(path: typing.Union[str, pathlib.Path]='.',
              ext=None,
              pattern=None,
              ignore_case=True,
              full_names=False,
              recursive=False,
              include_hidden=True) -> list:
    """
    List files in a given directory.

    path (str): absolute path to search for files in
    ext (str): optional file extension or list of extensions to filter resulting files by
    pattern (str): optional filter resulting files by matching regex pattern
    ignore_case (bool): do not consider case in when filtering for `pattern` parameter
    full_names (bool): return absolute filepaths
    recursive (bool): search recursively down the directory tree
    include_hidden (bool): include hidden files in resulting file list
    """
    owd = os.getcwd()
    os.chdir(path)

    if recursive:
        fpaths = []
        for root, dpaths, filenames in os.walk('.'):
            for f in filenames:
                fpaths.append(os.path.join(root, f).replace('./', ''))
    else:
        fpaths = [f for f in os.listdir() if os.path.isfile(f)]

    if not include_hidden:
        fpaths = [f for f in fpaths if not os.path.basename(f).startswith('.')]

    if pattern is not None:
        if ignore_case:
            fpaths = [f for f in fpaths if re.search(pattern, f, re.IGNORECASE)]
        else:
            fpaths = [f for f in fpaths if re.search(pattern, f)]

    if ext:
        ext = [x.lower() for x in ensurelist(ext)]
        ext = ['.' + x if not x.startswith('.') else x for x in ext]
        fpaths = [x for x in fpaths if os.path.splitext(x)[1].lower() in ext]

    if full_names:
        path_expand = os.getcwd() if path == '.' else path
        fpaths = [os.path.join(path_expand, f) for f in fpaths]

    os.chdir(owd)
    return fpaths


def ensurelist(val: typing.Any) -> list:
    """
    Accept a string or list and ensure that it is formatted as a list. If `val` is not a list,
    return [val]. If `val` is already a list, return as is.
    """
    return [val] if not isinstance(val, list) else val


def systime(as_string: bool=True, compact: bool=False) -> typing.Union[str, datetime.datetime]:
    """
    Get the current datetime, optionally formatted as a string.
    """
    if as_string:
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S' if compact else '%Y-%m-%d %H:%M:%S')
    else:
        assert not compact, 'Cannot set `compact` if returning a datetime object!'
        return datetime.datetime.now()


def find_binary(bin_name: str,
                additional_bin_paths: list=[],
                abort: bool=False,
                return_all: bool=False) -> typing.Union[str, list]:
    """
    Find system binary by name. If multiple binaries found, return the first one found unless `return_all` is True, in which case return a list of binaries found. If `abort` is True,
    then raise an error in the case that the desired binary is not found.

    Example:
        >>> find_binary('exiftool')
        # If exiftool installed
        '/usr/local/exiftool'

        # If exiftool installed in multiple locations and `return_all` is True
        ['/usr/local/exiftool', '/usr/bin/exiftool']

        # If exiftool installed in multiple locations and `return_all` is False
        /usr/local/exiftool

        # If exiftool not installed
        None
    """
    bin_paths = [x for x in sys.path if os.path.basename(x) in ['bin', 'lib']] + \
        ['/usr/bin', '/usr/local/bin']

    if len(additional_bin_paths):
        bin_paths = bin_paths + additional_bin_paths

    bin_paths = list(set(bin_paths))

    match = []
    for path in bin_paths:
        os.chdir(path)
        binaries = listfiles()
        for binary in binaries:
            if bin_name == binary:
                match_item = os.path.join(path, binary)
                match.append(match_item)
                logger.info(f'Matching binary found "{match_item}"')

    if len(match) > 1:
        if return_all:
            logger.warning(f"Multiple matches found for '{bin_name}', returning all: '{str(match)}'")
            return match
        else:
            logger.warning(f"Multiple matches found for '{bin_name}': {str(match)}, selected first")
            return match[0]

    elif len(match) == 0:
        if abort:
            raise FileNotFoundError(f"No matching binaries found for '{bin_name}'")
        else:
            logger.warning('No matching binaries found, returning None')
        return None

    return match[0]


def syscmd(cmd: typing.Union[str, list], encoding: str='') -> typing.Union[str, int]:
    """
    Runs a command on the system, waits for the command to finish, and then returns the
    text output of the command. If the command produces no text output, the command's
    return code will be returned instead. Optionally decode output bytestring.
    """
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)

    p.wait()
    output = p.stdout.read()

    if len(output) > 1:
        if encoding > '' and isinstance(output, bytes):
            return output.decode(encoding)
        else:
            return output
    else:
        logger.warning('Length of `output` is <=1, returning the process returncode')

        return p.returncode
