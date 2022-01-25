"""Module stop_watch.

=========
StopWatch
=========

The StopWatch class can be used during testing to start a clock, pause
for a certain amount of time relative to the started clock, and then
stop the clock and get the elapsed time.

:Example: verify timing of event

>>> import threading
>>> import time
>>> from scottbrian_utils.stop_watch import StopWatch
>>> def main() -> None:
...     def f1():
...         print('f1 entered')
...         stop_watch.start_clock(clock_iter=1)
...         print('f1 about to wait')
...         f1_event.wait()
...         print('f1 back from wait')
...         assert 2.5 <= stop_watch.duration() <= 2.6
...         print('f1 exiting')
...     print('mainline entered')
...     stop_watch = StopWatch()
...     f1_thread = threading.Thread(target=f1)
...     f1_event = threading.Event()
...     print('mainline about to start f1')
...     f1_thread.start()
...     stop_watch.pause(2.5, clock_iter=1)
...     print('mainline about to set f1_event')
...     f1_event.set()
...     f1_thread.join()
...     print('mainline exiting')
>>> main()
mainline entered
mainline about to start f1
f1 entered
f1 about to wait
mainline about to set f1_event
f1 back from wait
f1 exiting
mainline exiting


The stop_watch module contains:

    1) StopWatch class with methods:

       a. duration
       b. pause
       c. start_clock

"""

########################################################################
# Standard Library
########################################################################
import threading
import time
from typing import Final, Optional, Type, TYPE_CHECKING, Union

########################################################################
# Third Party
########################################################################

########################################################################
# Local
########################################################################

########################################################################
# type aliases
########################################################################
IntFloat = Union[int, float]
OptIntFloat = Optional[IntFloat]


########################################################################
# StopWatch Exceptions classes
########################################################################
class StopWatchError(Exception):
    """Base class for exception in this module."""
    pass


########################################################################
# StopWatch Class
########################################################################
class StopWatch:
    """StopWatch class for testing.

    The StopWatch class is used to assist in the testing of
    multi-threaded functions. It provides a set of methods that help
    with verification of timed event. The test case setup
    involves a mainline thread that starts one or more remote threads.
    The start_clock and duration methods are used to verify event times.

    """

    GET_CMD_TIMEOUT: Final[float] = 3.0

    ####################################################################
    # __init__
    ####################################################################
    def __init__(self) -> None:
        """Initialize the object."""
        self.clock_lock = threading.Lock()
        self.start_time: float = 0.0
        self.previous_start_time: float = 0.0
        self.clock_in_use = False
        self.clock_iter = 0

    ####################################################################
    # repr
    ####################################################################
    def __repr__(self) -> str:
        """Return a representation of the class.

        Returns:
            The representation as how the class is instantiated

        :Example: repr of StopWatch

        >>> from scottbrian_utils.stop_watch import StopWatch
        >>> stop_watch = StopWatch()
        >>> repr(stop_watch)
        'StopWatch()'

        """
        if TYPE_CHECKING:
            __class__: Type[StopWatch]
        classname = self.__class__.__name__
        parms = ''

        return f'{classname}({parms})'

    ####################################################################
    # pause
    ####################################################################
    def pause(self,
              seconds: IntFloat,
              clock_iter: int) -> None:
        """Sleep for the number of input seconds relative to start_time.

        Args:
            seconds: number of seconds to pause from the start_time for
                       the given clock_iter.
            clock_iter: clock clock_iter to pause on

        Notes:
            1) The clock_iter is used to identify the clock that is
               currently in use. A remote thread wants to pause
               for a given number of seconds relative to the StopWatch
               start_time for a given iteration of the clock. We will do
               a sleep loop until the given clock_iter matches
               the StopWatch clock_iter.

        """
        while clock_iter != self.clock_iter:
            time.sleep(0.1)

        remaining_seconds = seconds - (time.time() - self.start_time)
        if remaining_seconds > 0:
            time.sleep(remaining_seconds)

    ####################################################################
    # start_clock
    ####################################################################
    def start_clock(self,
                    clock_iter: int) -> None:
        """Set the start_time to the current time.

        Args:
            clock_iter: clock_iter to set for the clock
        """
        while True:
            with self.clock_lock:
                if not self.clock_in_use:  # if clock is free to use
                    self.clock_in_use = True  # claim for us
                    break
            time.sleep(0.01)  # wait until we can have the clock

        self.start_time = time.time()
        self.clock_iter = clock_iter

    ####################################################################
    # duration
    ####################################################################
    def duration(self) -> float:
        """Return the number of seconds from the start_time.

        Returns:
            number of seconds from the start_time
        """
        ret_duration = time.time() - self.start_time
        # no need to get clock_lock to reset the clock_in_use flag
        self.clock_in_use = False  # make available to others
        return ret_duration
