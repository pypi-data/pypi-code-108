"""
Standby state machine.

"""
from abc import ABCMeta, abstractproperty

from microcosm_logging.decorators import logger

from microcosm_daemon.sleep_policy import SleepNow


class StandByGuard:
    """
    State wrapper for a standby-enabled daemon.

    Calls state and then checks condition.

    """
    def __init__(self, next_state, condition, standby_timeout):
        self.next_state = next_state
        self.condition = condition
        self.standby_timeout = standby_timeout

    def __str__(self):
        return str(self.next_state)

    def __call__(self, graph):
        """
        Invoke the wrapped state and then check the standby condition.

        """
        try:
            result = self.next_state(graph)
        except Exception:
            result = None
            should_standby = self.condition(graph)
            if not should_standby:
                raise
            # NB: we may swallow an error here, but this is preferable to not standing by
        else:
            should_standby = self.condition(graph)

        next_state = result or self.next_state

        if should_standby:
            return StandByState(next_state, self.condition, self.standby_timeout, initial=True)

        return StandByGuard(next_state, self.condition, self.standby_timeout)


@logger
class StandByState:
    """
    State for a daemon that is in standby.

    Remains in standby until condition is met.

    """
    def __init__(self, next_state, condition, standby_timeout, initial=False):
        self.next_state = next_state
        self.condition = condition
        self.standby_timeout = standby_timeout
        self.initial = initial

    def __str__(self):
        return "standby"

    def __call__(self, graph):
        """
        Check the standby condition before advancing to the next state.

        """
        should_standby = self.condition(graph)
        if should_standby:
            if self.initial:
                self.logger.info("Standing by...")
                self.initial = False
            raise SleepNow(self.standby_timeout)

        self.logger.info("Starting up...")
        return StandByGuard(self.next_state, self.condition, self.standby_timeout)


class StandByMixin(metaclass=ABCMeta):
    """
    Mixin for a daemon to inject standby logic.

    """
    @abstractproperty
    def standby_condition(self):
        """
        Define a stand by condition.

        Should return a function that takes a graph and returns boolean.

        """
        pass

    @property
    def standby_timeout(self):
        """
        Define the sleep interface while in standby.

        Defaults to 1s; longer sleep intervals will delay both coming out of standby
        and interrupting/terminating the daemon (depending on signal handling).

        """
        return 1.0

    @property
    def initial_state(self):
        return StandByState(self, self.standby_condition, self.standby_timeout, initial=True)
