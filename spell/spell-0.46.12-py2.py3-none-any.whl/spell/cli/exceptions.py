from contextlib import contextmanager

import click
import requests.exceptions

from spell.cli.log import logger


CLICK_CLI_USAGE_ERROR = 2
SPELL_INVALID_CONFIG = 3
SPELL_INVALID_WORKSPACE = 4
SPELL_INVALID_COMMIT = 5
SPELL_BAD_REPO_STATE = 6


class ExitException(click.ClickException):
    def __init__(self, message, exit_code=None):
        self.exit_code = 1 if exit_code is None else exit_code
        super(ExitException, self).__init__(message)

    def show(self):
        logger.error(self.message)


class NotFoundException(ExitException):
    def __init__(self, message):
        super(ExitException, self).__init__(message)


@contextmanager
def api_client_exception_handler():
    # TODO(justin): Resolve the circular dependencies requiring these imports
    from spell.api.exceptions import ClientException, UnauthorizedRequest, UnauthorizedClient
    import spell.cli.utils.sentry as sentry

    try:
        yield
    except UnauthorizedClient as e:
        raise ExitException(e.message)
    except UnauthorizedRequest as e:
        raise ExitException(
            e.message if e.message else 'Login session has expired. Please log in again ("spell login").'
        )
    except ClientException as e:
        exception = getattr(e, "exception", None)
        if not exception:
            raise ExitException(e.message)
        # we expect connection errors for no internet connectivity that are not ProxyErrors or SSLErrors
        if isinstance(exception, requests.exceptions.ConnectionError) and not isinstance(
            exception, (requests.exceptions.ProxyError, requests.exceptions.SSLError)
        ):
            raise ExitException("Can't reach Spell. Please check your internet connection.")
        # unexpected Client Exception -- tell Spell
        sentry.capture_exception(e)
        raise ExitException(e.message)
