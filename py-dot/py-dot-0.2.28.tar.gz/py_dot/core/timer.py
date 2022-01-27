from threading import Thread, Event
from time import sleep
from typing import Callable


class TimerEvent(Event):
    """Timer Operator
    """

    def __init__(self):
        self._event = Event()

    def clear(self):
        """ Stop the Timer"""
        self._event.set()


def set_timeout(callback: Callable, delay: int, daemon=False) -> TimerEvent:
    """ Set Timer to Run after delay

    Print after 3s:
    >>> def foo(timer_: TimerEvent):
    ...     print('foo')
    ... timer = set_timeout(foo, 3)


    Disable Timer:
    >>> timer.clear()
    """

    def set_timeout_thread(event_: TimerEvent):
        sleep(delay)
        if not event_.is_set():
            callback()

    event = TimerEvent()
    thread = Thread(target=set_timeout_thread, args=(event,), daemon=daemon)
    thread.start()

    return event


def set_interval(callback: Callable, delay: int, daemon=False):
    """ Set Timer to Run per delay

    Print per 3s:
    >>> def foo(timer_: TimerEvent, index: int):
    ...     print('foo')
    ... timer = set_interval(foo, 3)


    Disable Timer:
    >>> timer.clear()
    """

    def set_interval_thread(event_: TimerEvent):
        index = 0
        while not event_.is_set():
            sleep(delay)
            callback(event, index)
            index += 1

    event = TimerEvent()
    thread = Thread(target=set_interval_thread, args=(event,), daemon=daemon)
    thread.start()

    return thread


def timeout(delay: int, daemon=False):
    """ set_timeout sugar decorator

    Print after 3s
    >>> @timeout(3)
    ... def foo(timer: TimerEvent):
    ...     print('foo')

    Disable Timer:
    >>> foo.clear()
    """

    def set_timeout_decorator(callback: Callable):
        return set_timeout(callback, delay, daemon)

    return set_timeout_decorator


def interval(delay: int, daemon=False):
    """ set_interval sugar decorator

    Print per 3s
    >>> @interval(3)
    ... def foo(timer: TimerEvent, index: int):
    ...     print('foo')

    Disable Timer:
    >>> foo.clear()
    """

    def set_interval_decorator(callback: Callable):
        return set_interval(callback, delay, daemon=daemon)

    return set_interval_decorator
