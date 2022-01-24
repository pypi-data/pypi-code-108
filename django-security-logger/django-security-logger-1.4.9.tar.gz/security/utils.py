import re
from importlib import import_module
from io import StringIO
from time import time

from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import now

from .config import settings


def get_throttling_validators(name):
    try:
        return getattr(import_module(settings.DEFAULT_THROTTLING_VALIDATORS_PATH), name)
    except (ImportError, AttributeError):
        raise ImproperlyConfigured('Throttling validator configuration {} is not defined'.format(name))


def remove_nul_from_string(value):
    return value.replace('\x00', '')


def is_atty_string(s):
    return bool(re.search(r'^' + re.escape('\x1b[') + r'\d+m$', s))


class LogStringIO(StringIO):

    BOLD = '\x1b[1m'
    RESET = '\x1b[0m'

    def __init__(self, flush_callback=None, flush_timeout=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_closed = False
        self._last_newline = 0
        self._flush_callback = flush_callback
        self._write_time = True
        self._last_flush_time = time()
        self._flush_timeout = settings.LOG_STRING_IO_FLUSH_TIMEOUT if flush_timeout is None else flush_timeout

    def _flush(self, force=False):
        if self._flush_callback and (force or time() - self._last_flush_time > self._flush_timeout):
            self._flush_callback(self)
            self._last_flush_time = time()

    def write(self, s):
        if not self._is_closed:
            lines = s.split('\n')

            for i, line in enumerate(lines):
                cursor_first = True
                for cursor_block in line.split('\r'):
                    if not cursor_first:
                        self.seek(self._last_newline)
                        self.truncate()
                        self._write_time = True
                    cursor_first = False

                    if self._write_time and not is_atty_string(cursor_block):
                        cursor_block = '{}{}[{}]{} {}'.format(
                            self.RESET, self.BOLD, now().strftime('%d-%m-%Y %H:%M:%S'), self.RESET, cursor_block
                        )
                        self._write_time = False

                    super().write(cursor_block)

                if i != len(lines) - 1:
                    super().write('\n')
                    self._last_newline = self.tell()
                    self._write_time = True

            self._flush()

    def isatty(self):
        return True

    def close(self):
        self._is_closed = True
        self._flush(force=True)
        super().close()


class TeeStringIO:
    """
    StringIO that additionally writes to another stream(s).
    """
    ANSI_ESCAPE_REGEX = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def __init__(self, out, log_stream):
        self._out = out
        self._log_stream = log_stream
        self._last_newline = 0
        super().__init__()

    def write(self, s):
        if self.isatty():
            self._out.write(s)
        else:
            self._out.write(self.ANSI_ESCAPE_REGEX.sub('', s))
        self._log_stream.write(s)

    def __getattr__(self, name):
        return getattr(self._out, name)

    def isatty(self):
        return hasattr(self._out, 'isatty') and self._out.isatty()

    def flush(self):
        self._out.flush()
        self._log_stream.flush()


def regex_sub_groups_global(pattern, repl, string):
    """
    Globally replace all groups inside pattern with `repl`.
    If `pattern` doesn't have groups the whole match is replaced.
    """
    for search in reversed(list(re.finditer(pattern, string))):
        for i in range(len(search.groups()), 0 if search.groups() else -1, -1):
            start, end = search.span(i)
            string = string[:start] + repl + string[end:]
    return string


def update_logged_request_data(request, related_objects=None, slug=None, extra_data=None):
    input_request_logger = getattr(request, 'input_request_logger', None)
    if input_request_logger:
        if related_objects:
            input_request_logger.add_related_objects(*related_objects)
        if slug:
            input_request_logger.set_slug(slug)
        if extra_data:
            input_request_logger.update_extra_data(extra_data)
