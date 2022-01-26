"""
Sleep policy.

"""
from time import sleep

from microcosm.api import defaults
from microcosm.config.validation import typed
from microcosm_logging.decorators import logger


class SleepNow(Exception):

    def __init__(self, sleep_timeout=None):
        self.sleep_timeout = sleep_timeout


@logger
class SleepPolicy:
    """
    Determine whether to sleep before processing another state function.

    """
    def __init__(self, default_sleep_timeout):
        self.default_sleep_timeout = default_sleep_timeout

    def sleep(self, sleep_timeout):
        """
        Patch target for sleeping.

        """
        sleep(sleep_timeout)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is SleepNow:
            self.sleep(value.sleep_timeout or self.default_sleep_timeout)
            return True


@defaults(
    default_sleep_timeout=typed(float, 0.5),
)
def configure_sleep_policy(graph):
    return SleepPolicy(
        default_sleep_timeout=graph.config.sleep_policy.default_sleep_timeout,
    )
