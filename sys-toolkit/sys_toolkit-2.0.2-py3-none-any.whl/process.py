"""
List and manipulate OS processes
"""

import re

from datetime import datetime

from .collection import CachedMutableSequence
from .exceptions import CommandError
from .subprocess import run_command_lineoutput

DEFAULT_CACHE_SECONDS = 5

TIME_FORMATS = (
    '%a %b %d %H:%M:%S %Y',
    '%a %d %b %H:%M:%S %Y',
)

STARTED_FIELD = 'lstart'
COMMAND_FIELD = 'command'
PS_FIELDS = (
    STARTED_FIELD,
    'ppid',
    'pid',
    'ruid',
    'rgid',
    'ruser',
    'vsz',
    'rss',
    'state',
    'tdev',
    'time',
    COMMAND_FIELD,
)
STRING_FIELDS = (
    COMMAND_FIELD,
    'ruser',
    'user',
    'time',
    'tdev',
    'state',
)
USERID_FIELDS = (
    'ruid',
    'uid'
)
USERNAME_FIELDS = (
    'ruser',
    'user'
)


def parse_datetime(value):
    """
    Parse a datetime value matching time formats
    """
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except (TypeError, ValueError):
            pass
    return None


class Process:
    """
    Process in process list as parsed from ps output line
    """
    pid = None
    command = None
    started = None

    def __init__(self, processes, line):
        self.__processes__ = processes
        self.__parse_line__(line)

    def __repr__(self):
        return f'{self.username} {self.pid} {self.command}'

    def __parse_started__(self, line):
        """
        Parse 'started' (lstart) timestamp from line
        """
        values = line.split()

        if STARTED_FIELD not in self.__processes__.attributes:
            self.started = None
            return values

        date_start = self.__processes__.attributes.index(STARTED_FIELD)
        date_end = date_start + 5
        self.started = parse_datetime(' '.join(values[date_start:date_end]))
        # Trim date data out of parsed values
        return values[:date_start] + values[date_end:]

    def __parse_line__(self, line):
        """
        Parse process info from line
        """
        values = self.__parse_started__(line)
        attributes = [
            attr
            for attr in self.__processes__.attributes
            if attr != STARTED_FIELD
        ]
        for index, attr in enumerate(attributes):
            try:
                if attr == COMMAND_FIELD:
                    value = ' '.join(values[index:])
                else:
                    value = values[index]
            except IndexError:
                value = None

            if value is not None and attr not in STRING_FIELDS:
                try:
                    value = int(value)
                except ValueError:
                    pass
            setattr(self, attr, value)

    @property
    def user_id(self):
        """
        User ID
        """
        for attr in USERNAME_FIELDS:
            if hasattr(self, attr):
                return getattr(self, attr)
        return None

    @property
    def username(self):
        """
        Username
        """
        for attr in USERNAME_FIELDS:
            if hasattr(self, attr):
                return getattr(self, attr)
        return None


class Processes(CachedMutableSequence):
    """
    List of operating system processes
    """

    def __init__(self, attributes=PS_FIELDS, cache_age_seconds=DEFAULT_CACHE_SECONDS):
        self.__max_age_seconds__ = cache_age_seconds
        self.attributes = attributes

    @property
    def command(self):
        """
        CLI command to run to get process list
        """
        return ['ps', '-wwaxo', ','.join(self.attributes)]

    def filter(self, *args, **kwargs):
        """Filter processes

        Filters entries matching given filters. Filter must be a
        - list of key=value strings
        - dictionary with valid keys
        """
        filters = []
        try:
            filters = [(key, pattern) for x in args for key, pattern in x.split('=', 1)]
        except ValueError as error:
            raise CommandError(f'Invalid process filter list: {args}: {error}') from error
        filters.extend(kwargs.items())

        filtered = []
        for process in self:
            matches = True
            for key, pattern in filters:
                if not hasattr(process, key):
                    raise CommandError(f'Invalid filter key: {key}')
                if not re.compile(str(pattern)).match(str(getattr(process, key))):
                    matches = False
                    break
            if matches:
                filtered.append(process)

        return filtered

    def update(self):
        """
        Update list of processes visible to current user
        """
        self.clear()

        self.__start_update__()
        lines, errors = run_command_lineoutput(*self.command)
        if errors:
            self.__reset__()
            raise CommandError(f'Error running {self.command}')

        # Skip header line
        for line in lines[1:]:
            process = Process(self, line)
            self.append(process)

        self.__finish_update__()
