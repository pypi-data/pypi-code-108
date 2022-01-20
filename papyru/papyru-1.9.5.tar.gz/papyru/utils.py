import logging
from contextlib import contextmanager
from datetime import datetime
from enum import Enum, unique
from os import getpid
from unittest.mock import patch
from uuid import uuid4

from papyru.logger import log_info

_logger = logging.getLogger(__name__)


@unique
class PAPEnum(Enum):
    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


@contextmanager
def limited_runtime(timeout):
    '''
    Checks if runtime is left.

    Example:

        .. code-block:: python

            with limited_runtime(
                    datetime.timedelta(minutes=MAX_RUNTIME_MINUTES)
            ) as has_runtime_left:
                while has_runtime_left():
                    do_something()
                    sleep(1)
    '''

    start_time = datetime.now()

    def has_runtime_left():
        return (datetime.now() - start_time) < timeout

    try:
        yield has_runtime_left
    finally:
        pass


def parse_bool(value):
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    elif isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    elif isinstance(value, int):
        return value == 1
    elif isinstance(value, float):
        return int(value) == 1
    else:
        raise TypeError('cannot parse bool from "%s".' % value)


def setup_request_ids():
    if setup_request_ids._already_patched:
        return
    else:
        setup_request_ids._already_patched = True

    import requests

    class PatchedSession(requests.sessions.Session):
        def prepare_request(self, request):
            request.headers = {**(request.headers or {}),
                               'pap-request-id': str(uuid4())}

            log_info('sending request %s: %s %s' % (
                request.headers.get('pap-request-id'),
                request.method,
                request.url))

            return super().prepare_request(request)

    requests.sessions.Session = PatchedSession


setup_request_ids._already_patched = False


def silent_log_commit(self, item):
    pass


def make_silent_testcase(TestCaseClass):
    class Impl(TestCaseClass):
        @patch('papyru.logger_stdout.StdoutSink.commit', silent_log_commit)
        def run(self, *args, **kwargs):
            logger = logging.getLogger()
            _loglevel = logger.getEffectiveLevel()

            try:
                logger.setLevel(logging.CRITICAL + 1)

                result = super().run(*args, **kwargs)

                logger.setLevel(_loglevel)

                return result

            finally:
                logger.setLevel(_loglevel)
    return Impl


def log(message, level='info'):
    getattr(_logger, level)('[%d]: %s' % (getpid(), message))
