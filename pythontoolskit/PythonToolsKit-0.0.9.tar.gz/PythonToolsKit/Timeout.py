#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> from Timeout import *
>>> from time import sleep
>>> class A:
...     def __init__(self):
...         self.a = "a"
...
>>> @thread_timeout(2)
... def test():
...     while 1:
...         print("pass")
...         sleep(1)
...
>>> test()
pass
pass
pass
Traceback (most recent call last):
    ...
TimeoutError: TimeoutError in "test"
Traceback (most recent call last):
    ...
KeyboardInterrupt
>>> @thread_timeout(2)
... def test():
...     print("pass")
...     sleep(1)
...     return A()
...
>>> test()
pass
<__main__.A object at ...>
>>> @signal_timeout(2)
... def test():
...     while 1:
...         print("pass")
...         sleep(1)
...
>>> test()
pass
pass
pass
Traceback (most recent call last):
    ...
TimeoutError
>>> @signal_timeout(2)
... def test():
...     print("pass")
...     sleep(1)
...     return A()
...
>>> test()
pass
<__main__.A object at ...>
>>> @process_timeout(2)
... def test():
...     print("pass")
...     sleep(1)
...     return A()
...
>>> test()
pass
<__main__.A object at ...>
>>> @process_timeout(2)
... def test():
...     while 1:
...         print("pass")
...         sleep(1)
...
>>> test()
pass
pass
pass
Traceback (most recent call last):
    ...
TimeoutError: TimeoutError in "test"
Traceback (most recent call last):
    ...
KeyboardInterrupt
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["thread_timeout", "process_timeout"]

from sys import stderr, platform

is_linux = platform != "win32"

if is_linux:
    from signal import signal, setitimer, SIGALRM, ITIMER_REAL

from multiprocessing import Process, Queue, freeze_support
from collections.abc import Callable, Sequence
from sys import modules as sys_modules
from _thread import interrupt_main
from typing import Any, List, Dict
from traceback import format_exc
from os import getpid, environ
from threading import Timer
from functools import wraps

freeze_support()
current_pid: str = str(getpid())
pid: str = environ.setdefault("PID", current_pid)


def thread_quit_timeout(function_name: str) -> None:

    """
    This function raise a TimeoutError in the current
    thread and a KeyboardInterrupt in the main thread.
    """

    try:
        raise TimeoutError(f'TimeoutError in "{function_name}"')
    except TimeoutError:
        stderr.write(format_exc())
        interrupt_main()


def thread_timeout(seconds: int) -> Callable:

    """
    This decorator implements a function timeout.
    """

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs) -> Any:
            timer = Timer(
                seconds, thread_quit_timeout, args=(function.__name__,)
            )
            timer.start()

            try:
                value = function(*args, **kwargs)
            finally:
                timer.cancel()

            return value

        return wrapper

    return decorator


class _ProcessObject:

    """
    This class implements the process object to
    raise TimeoutError.
    """

    def __init__(
        self,
        method: Callable,
        queue: Queue,
        args: Sequence[Any],
        kwargs: Dict[str, Any],
    ):
        self.method = method
        self.queue = queue
        self.args = args
        self.kwargs = kwargs


def _process_timeout(process_obj: _ProcessObject) -> None:

    """
    This function puts state and output or error in Queue.
    """

    put = process_obj.queue.put

    try:
        put(
            (True, process_obj.method(*process_obj.args, **process_obj.kwargs))
        )
    except Exception as error:
        put((False, error))


def process_timeout(seconds: int) -> Callable:

    """
    This decorator implements a function timeout.
    """

    def decorator(function: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:

            if type(function) == classmethod:
                args = args[1:]
                real_function = function.__func__
            else:
                real_function = function

            name = real_function.__qualname__ or real_function.__name__
            module = real_function.__module__

            elem = sys_modules[module]

            for elem_name in name.split("."):
                parent = elem
                elem = getattr(elem, elem_name)

            setattr(parent, elem_name, real_function)

            queue = Queue(1)
            process_obj = _ProcessObject(real_function, queue, args, kwargs)
            process = Process(target=_process_timeout, args=(process_obj,))

            process.start()
            process.join(seconds)

            process.terminate()
            process.kill()
            process.close()

            setattr(parent, elem_name, elem)

            if not queue.empty():
                flag, value = queue.get()
            else:
                flag = None
                value = TimeoutError(
                    f'"{name}" takes more than {seconds} seconds to run.'
                )

            if flag:
                return value

            raise value

        if current_pid == pid:
            return wrapper
        else:
            return function

    return decorator


if is_linux:
    __all__.append("signal_timeout")

    def signal_quit_timeout(signum, frame) -> None:

        """
        This function raise a TimeoutError.
        """

        raise TimeoutError()

    def signal_timeout(seconds: int) -> Callable:

        """
        This decorator implements a function timeout.
        """

        def decorator(function: Callable) -> Callable:
            @wraps(function)
            def wrapper(*args, **kwargs) -> Callable:
                old = signal(SIGALRM, signal_quit_timeout)
                setitimer(ITIMER_REAL, seconds)

                try:
                    value = function(*args, **kwargs)
                finally:
                    signal.setitimer(ITIMER_REAL, 0)
                    signal.signal(SIGALRM, old)

                return value

            return wrapper

        return decorator
