import inspect
import traceback
import warnings
from enum import EnumMeta
from functools import wraps
from multiprocessing import Event
from threading import Thread
import threading
from typing import Dict
from time import time
import time
from functools import partial
from debug_utils import LineTimer


class PeriodicTask(Thread):
    def __init__(self, func, interval, args=None, verbose=False, printer=None, name_prefix=None):
        task_name = f'PeriodicTask-{func.__name__}'
        self.full_task_name = task_name if name_prefix is None else f'{name_prefix}-{task_name}'
        super().__init__(name=self.full_task_name)

        self.func = func if args is None else partial(func, args=args)
        self.func_name = self.func.__name__
        self.interval = interval
        self.verbose = verbose
        self.waiter_event = threading.Event()
        self.timer = LineTimer()

        # define printer function
        if verbose is False:
            def false_printer(*args):
                pass

            printer = false_printer
        if printer is None:
            self.printer = print
        else:
            self.printer = printer

        self.state = 'init'
        self.wait_for_command = Event()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            traceback.print_tb(exc_tb)
            warnings.warn(f'In PeriodicTask(func={self.func_name}) __exit__ - {exc_type} {exc_val}')
        self.stop()

    def run(self):
        self.state = 'running'

        while True:
            self.waiter_event.clear()

            if self.state == 'running':
                self.timer.start()
                self.func()
                self.printer(f'Periodic task iteration completed! - {self.full_task_name}, {time.time()}')

            elif self.state == 'pause':
                self.printer(f'Periodic task paused! - {self.full_task_name}, {time.time()}')
                self.timer.stop()
                self.waiter_event.wait()
                self.printer(f'Periodic task resumed! - {self.full_task_name}, {time.time()}')

            elif self.state == 'stopped':
                self.printer(f'Periodic task stopped! - {self.full_task_name}, {time.time()}')
                return

            self.waiter_event.wait(timeout=self.interval - self.timer.stop())

    def pause(self):
        self.state = 'paused'
        self.waiter_event.set()

    def resume(self):
        self.state = 'running'
        self.waiter_event.set()

    def stop(self):
        self.state = 'stopped'
        self.waiter_event.set()


class WrappingThread(Thread):

    def __init__(self, func, *args, **kwargs):
        super().__init__(
            daemon=True,
            name=f'in_new_thread-{func.__name__}'
        )

        self.calling_func = inspect.stack()[1].function
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.func(*self.args, **self.kwargs)


def in_new_thread(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> Thread:
        new_thread = WrappingThread(func, *args, **kwargs)
        new_thread.calling_func = inspect.stack()[1].function
        new_thread.start()
        return new_thread

    return wrapper


class JoinableState:
    """
    Contains several events created by args, this class clears all events when one is being set
    (so only one event should be set at each given time)
    """

    def __init__(self, iterable, default):
        if isinstance(iterable, EnumMeta):
            self._events: Dict[int, Event] = {enum.value: Event() for enum in iterable}
            self._value2name: Dict[int, str] = {enum.value: enum.name for enum in iterable}
            self.set(value=default)
        elif all(type(val) == str for val in iterable):
            self._events: Dict[int, Event] = {ind: Event() for ind, _ in enumerate(iterable)}
            self._value2name: Dict[int, str] = {ind: name for ind, name in enumerate(iterable)}
            name2value = {name: ind for ind, name in self._value2name.items()}
            self.set(value=name2value[default])
        else:
            raise TypeError('Not Supoorted')

    @property
    def name(self):
        cur_value = self.value
        if cur_value is None:
            return None
        else:
            return self._value2name[cur_value]

    @property
    def value(self):
        for value, event in self._events.items():
            if event.is_set():
                return value
        else:
            return None

    @value.setter
    def value(self, value):
        self.set(value)

    def clear(self, value=None):
        if value is None:
            for event in self._events.values():
                event.clear()
        else:
            self._events[value].clear()

    def set(self, value: int):
        self.clear()
        self._events[value].set()

    def wait(self, value, timeout=None, raise_error=False):
        is_success = self._events[value].wait(timeout=timeout)
        if not is_success and raise_error:
            raise TimeoutError(f'In JoinableState: event {value} timed out')
        else:
            return is_success
