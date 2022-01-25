"""Module timer.

=====
Timer
=====

The Timer class can be used to detect when a process has exceeded a
specified amount of time.

:Example: create a timer and use in a loop

>>> from scottbrian_utils.timer import Timer
>>> import time
>>> def example1() -> None:
...     print('example1 entered')
...     timer = Timer(timeout=3)
...     for idx in range(10):
...         print(f'idx = {idx}')
...         time.sleep(1)
...         if timer.is_expired():
...             print('timer has expired')
...             break
...     print('example1 exiting')
>>> example1()
example1 entered
idx = 0
idx = 1
idx = 2
timer has expired
example1 exiting


The timer module contains:

    1) Timer class with methods:

       a. is_expired

"""

########################################################################
# Standard Library
########################################################################
import time
from typing import Optional, Union

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
# Timer class exceptions
########################################################################
class TimerError(Exception):
    """Base class for exceptions in this module."""
    pass


########################################################################
# Timer Class
########################################################################
class Timer:
    """Timer class."""
    ####################################################################
    # __init__
    ####################################################################
    def __init__(self,
                 timeout: OptIntFloat = None,
                 default_timeout: OptIntFloat = None
                 ) -> None:
        """Initialize a timer object.

        Args:
            timeout: value to use for timeout
            default_timeout: value to use if timeout is None

        Example: class with a method that uses Timer

        >>> class A:
        ...     def __init__(self):
        ...         self.a = 1
        ...     def m1(self, sleep_time: float) -> bool:
        ...         timer = Timer(timeout=1)
        ...         time.sleep(sleep_time)
        ...         if timer.is_expired():
        ...             return False
        ...         return True
        >>> def example2() -> None:
        ...     print('example2 entered')
        ...     my_a = A()
        ...     print(my_a.m1(0.5))
        ...     print(my_a.m1(1.5))
        ...     print('example2 exiting')
        >>> example2()
        example2 entered
        True
        False
        example2 exiting

        Example: class with a method that uses Timer and timeout parm

        >>> class A:
        ...     def __init__(self):
        ...         self.a = 1
        ...     def m1(self, sleep_time: float, timeout: float) -> bool:
        ...         timer = Timer(timeout=timeout)
        ...         time.sleep(sleep_time)
        ...         if timer.is_expired():
        ...             return False
        ...         return True
        >>> def example3() -> None:
        ...     print('example3 entered')
        ...     my_a = A()
        ...     print(my_a.m1(sleep_time=0.5, timeout=0.7))
        ...     print(my_a.m1(sleep_time=1.5, timeout=1.2))
        ...     print(my_a.m1(sleep_time=1.5, timeout=1.8))
        ...     print('example3 exiting')
        >>> example3()
        example3 entered
        True
        False
        True
        example3 exiting

        Example: class with default timeout and method with timeout parm

        >>> class A:
        ...     def __init__(self, default_timeout: float):
        ...         self.a = 1
        ...         self.default_timeout = default_timeout
        ...     def m1(self,
        ...            sleep_time: float,
        ...            timeout: Optional[float] = None) -> bool:
        ...         timer = Timer(timeout=timeout,
        ...                       default_timeout=self.default_timeout)
        ...         time.sleep(sleep_time)
        ...         if timer.is_expired():
        ...             return False
        ...         return True
        >>> def example4() -> None:
        ...     print('example4 entered')
        ...     my_a = A(default_timeout=1.2)
        ...     print(my_a.m1(sleep_time=0.5))
        ...     print(my_a.m1(sleep_time=1.5))
        ...     print(my_a.m1(sleep_time=0.5, timeout=0.3))
        ...     print(my_a.m1(sleep_time=1.5, timeout=1.8))
        ...     print(my_a.m1(sleep_time=1.5, timeout=0))
        ...     print('example4 exiting')
        >>> example4()
        example4 entered
        True
        False
        False
        True
        True
        example4 exiting

        Notes:
            1) The reason for having both a timeout parm and a
               default_timeout parm is needed as follows: Some classes
               are instantiated with a default timeout for use in
               methods that have a timeout parm. The method timeout arg
               has priority and can be specified as negative or zero to
               indicate no timeout is to be in effect, or with a
               positive value to be used as the timeout value, or as
               None (explicitly or implicitly). When None is detected,
               then the method will use the default timeout for the
               class. The methods can thus simply instantiate a Timer
               and pass in both the timeout and the default timeout
               values, and Timer will sort things out and use the
               intended value as described above.

        """
        self.start_time = time.time()
        # cases:
        # 1) timeout = None and default_timeout = None
        #    result: is_expired will always return False (no timeout)
        # 2) timeout = None and default_timeout <= 0
        #    result: is_expired will always return False (no timeout)
        # 3) timeout = None and default_timeout > 0
        #    result: is_expired will return True if elapsed time is
        #            greater than default_timeout
        # 4) timeout <= 0 and default_timeout = None
        #    result: is_expired will always return False (no timeout)
        # 5) timeout <= 0 and default_timeout <= 0
        #    result: is_expired will always return False (no timeout)
        # 6) timeout <= 0 and default_timeout > 0
        #    result: is_expired will always return False (no timeout)
        # 7) timeout > 0 and default_timeout = None
        #    result: is_expired will return True if elapsed time is
        #            greater than timeout
        # 8) timeout > 0 and default_timeout <= 0
        #    result: is_expired will return True if elapsed time is
        #            greater than timeout
        # 9) timeout > 0 and default_timeout > 0
        #    result: is_expired will return True if elapsed time is
        #            greater than timeout
        #
        # summary: is_expired can return True only when timeout > 0 or
        #          when timeout = None and default_timeout > 0. All
        #          other cases will result in False, meaning a timeout
        #          will never happen. The _timeout variable is set
        #          here with either a positive value for the former,
        #          and with None for later.
        if timeout and timeout > 0:  # positive timeout takes precedent
            self._timeout: OptIntFloat = timeout
        elif (timeout is None) and (default_timeout and default_timeout > 0):
            self._timeout = default_timeout
        else:
            self._timeout = None

    ####################################################################
    # remaining_time
    ####################################################################
    def remaining_time(self) -> OptIntFloat:
        """Return the remaining timer time.

        Returns:
            remaining time of the timer

        Example: using remaining_time and is_expired

        >>> import threading
        >>> import time
        >>> from scottbrian_utils.timer import Timer
        >>> def f1(f1_event):
        ...     print('f1 entered')
        ...     time.sleep(1)
        ...     f1_event.set()
        ...     time.sleep(1)
        ...     f1_event.set()
        ...     time.sleep(1)
        ...     f1_event.set()
        ...     print('f1 exiting')
        >>> def example5() -> None:
        ...     print('example5 entered')
        ...     timer = Timer(timeout=2.5)
        ...     f1_event = threading.Event()
        ...     f1_thread = threading.Thread(target=f1,
        ...                                  args=(f1_event,))
        ...     f1_thread.start()
        ...     wait_result = f1_event.wait(
        ...         timeout=timer.remaining_time())
        ...     print(f'wait1 result = {wait_result}')
        ...     f1_event.clear()
        ...     print(f'remaining time = {timer.remaining_time():0.1f}')
        ...     print(f'timer expired = {timer.is_expired()}')
        ...     wait_result = f1_event.wait(
        ...         timeout=timer.remaining_time())
        ...     print(f'wait2 result = {wait_result}')
        ...     f1_event.clear()
        ...     print(f'remaining time = {timer.remaining_time():0.1f}')
        ...     print(f'timer expired = {timer.is_expired()}')
        ...     wait_result = f1_event.wait(
        ...         timeout=timer.remaining_time())
        ...     print(f'wait3 result = {wait_result}')
        ...     f1_event.clear()
        ...     print(f'remaining time = {timer.remaining_time():0.4f}')
        ...     print(f'timer expired = {timer.is_expired()}')
        ...     f1_thread.join()
        ...     print('example5 exiting')
        >>> example5()
        example5 entered
        f1 entered
        wait1 result = True
        remaining time = 1.5
        timer expired = False
        wait2 result = True
        remaining time = 0.5
        timer expired = False
        wait3 result = False
        remaining time = 0.0001
        timer expired = True
        f1 exiting
        example5 exiting


        Notes:
            1) The remaining time is calculated by subtracting the
               elapsed time from the timeout value originally supplied
               when the timer was instantiated. Depending on when the
               remaining time is requested, it could be such that the
               timeout value has been reached or exceeded and the true
               remaining time becomes zero or negative. The returned
               value, however, will never be zero or negative - it will
               be at least a value of 0.0001. Thus, the timeout value
               can not be used to determine whether the timer has
               expired since it will always show at least 0.0001 seconds
               remaining after the timer has truly expired. The
               is_expired method should be used to determine whether the
               timer has expired. The reason for this is that the
               intended use of remaining_time is to use it as a timeout
               arg that is passed into a service such as wait or a lock
               obtain. Many services interpret a value of zero or less
               as an unlimited timeout value, meaning it will never
               timeout. It is thus better to pass in a very small value
               and get an immediate timeout in these cases than to
               possibly wait forever.
            2) None is returned when the timer was originally
               instantiated with unlimited time.

        """
        if self._timeout:  # if not None
            # make sure not negative
            ret_timeout = max(0.0001,
                              self._timeout - (time.time() - self.start_time))
        else:
            ret_timeout = None
        return ret_timeout  # return value of remaining time for timeout

    ####################################################################
    # is_expired
    ####################################################################
    def is_expired(self) -> bool:
        """Return either True or False for the timer.

        Returns:
            True if the timer has expired, False if not

        Example: using is_expired

        >>> import time
        >>> from scottbrian_utils.timer import Timer
        >>> def example6() -> None:
        ...     print('example6 entered')
        ...     timer = Timer(timeout=2.5)
        ...     time.sleep(1)
        ...     print(f'timer expired = {timer.is_expired()}')
        ...     time.sleep(1)
        ...     print(f'timer expired = {timer.is_expired()}')
        ...     time.sleep(1)
        ...     print(f'timer expired = {timer.is_expired()}')
        ...     print('example6 exiting')
        >>> example6()
        example6 entered
        timer expired = False
        timer expired = False
        timer expired = True
        example6 exiting

        """
        if self._timeout and self._timeout < (time.time() - self.start_time):
            return True  # we timed out
        else:
            # time remaining, or timeout is None which never expires
            return False
