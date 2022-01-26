"""
Error handling policy.

"""
from logging import getLogger
from time import time

from microcosm.api import defaults
from microcosm.config.validation import typed


# nagios style health codes
HEALTH_OK = 0
HEALTH_WARN = 1
HEALTH_ERROR = 2


logger = getLogger("daemon.error_policy")


class ExitError(Exception):
    """
    Unconditionally exit the state machine.

    """
    pass


class FatalError(Exception):
    """
    Unconditionally exit the state machine.

    """
    pass


class ErrorPolicy:
    """
    Handle errors from state functions.

    """
    def __init__(self, strict, health_report_interval):
        self.strict = strict
        self.health_report_interval = health_report_interval
        self.errors = []
        self.health = self.compute_health()
        self.last_health_report_time = 0

    def compute_health(self):
        """
        Compute the current daemon health.

        """
        return HEALTH_OK if not self.errors else HEALTH_ERROR

    def should_report_health(self, new_health):
        """
        Should health be reported?

        True if health status changes or enough time elapses.

        """
        if self.health != new_health:
            return True
        return self.last_health_report_time + self.health_report_interval < time()

    def report_health(self, new_health):
        """
        Report health information to logs.

        """
        self.last_health_report_time = time()

        message = "Health is {}".format(
            new_health,
        )

        if self.health != new_health:
            logger.info(message)
        else:
            logger.debug(message)

        for error in self.errors:
            if isinstance(error, ExitError):
                continue
            logger.warn("Caught error during state evaluation: {}".format(error), exc_info=True)

    def maybe_report_health(self):
        """
        Conditionally report health information.

        """
        new_health = self.compute_health()
        if self.should_report_health(new_health):
            self.report_health(new_health)
        self.health = new_health

    def __enter__(self):
        # reset errors on every iteration
        self.errors = []
        return self

    def __exit__(self, type, value, traceback):
        if value:
            self.errors.append(value)
        self.maybe_report_health()
        return not self.strict and type not in (ExitError, FatalError)


@defaults(
    strict=False,
    health_report_interval=typed(float, 3.0),
)
def configure_error_policy(graph):
    return ErrorPolicy(
        strict=graph.config.error_policy.strict,
        health_report_interval=graph.config.error_policy.health_report_interval,
    )
