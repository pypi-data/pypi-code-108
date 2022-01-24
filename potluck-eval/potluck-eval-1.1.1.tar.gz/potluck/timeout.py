"""
Hacks in an attempt to permit running a function with an external time
limit. Only the Unix-specific SIGALRM method seems to work?

timeout.py
"""

import threading
import ctypes
import time
import signal

from . import logging


class TimeoutError(Exception):
    """
    Error generated when a time limit causes a function to be
    terminated.
    """
    pass


def with_threading_timeout(time_limit, function, args):
    """
    Attempts to run a function with a time_limit using a child thread and
    the timeout argument to `threading.Thread.join`. Note that running
    some kinds of code in a child thread can be disastrous (e.g., turtle
    graphics).
    """
    result = None

    class PayloadThread(threading.Thread):
        """
        A thread that runs a payload and has the ability to (attempt
        to) kill itself.
        """
        # TODO: Trying to run turtle code in a secondary thread crashes
        def run(self):
            """
            Runs the payload and smuggles out the result via a
            non-local variable.
            """
            nonlocal result, function, args
            try:
                result = function(*args)
            except TimeoutError:
                # TODO: Log more info here...?
                logging.log("Payload timed out.")

        def get_id(self):
            """
            Hack to get our thread ID (hidden threading module
            state).
            """
            if hasattr(self, "_thread_id"):
                return self._thread_id
            else:
                for tid, thread in threading._active.items():
                    if thread is self:
                        return tid

        def timeout(self):
            thread_id = self.get_id()
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                thread_id,
                ctypes.py_object(
                    TimeoutError(
                        f"Test took too long to run (more than"
                        f" {time_limit:.3f}s (in child thread)."
                    )
                )
            )
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                logging.log(
                    "Failed to raise timeout exception via ctypes!"
                )

    # Measure actual elapsed time
    start_time = time.monotonic()

    # Create our payload thread
    payload_thread = PayloadThread()
    payload_thread.start() # starts the payload thread

    # join, but only wait so long
    payload_thread.join(timeout=time_limit)

    # If it's still alive, we'll attempt to kill it and raise an
    # exception ourselves...
    if payload_thread.is_alive():
        payload_thread.timeout()
        elapsed = time.monotonic() - start_time
        raise TimeoutError(
            f"Test took too long to run (more than {time_limit:.3f}s"
            f"; actual time elapsed was {elapsed:.3f}s)."
        )

    # Return our result if we got here...
    return result


def with_sigalrm_timeout(time_limit, function, args):
    """
    Attempts to run a function with a time limit using signal's alarm
    functionality (which is unfortunately Unix-specific). If that
    functionality isn't available, it just runs the function without
    enforcing a timeout, but raises an exception if the function takes
    too long in the end.

    Note that this is NOT re-entrant: only one timer can be running at
    once. That's probably fine though...
    """
    # Record start time
    start_time = time.monotonic()

    if hasattr(signal, 'SIGALRM'):
        # We can enforce our time limit
        def handle_timeout(signum, frame):
            """
            Raises a TimeoutError since the signal will be generated when
            the time is up.
            """
            elapsed = time.monotonic() - start_time
            raise TimeoutError(
                f"Test took too long to run (more than {time_limit:.3f}s"
                f"; actual time elapsed was {elapsed:.3f}s)."
            )

        # Set up signal handler (we don't care about the old handler)
        _ = signal.signal(signal.SIGALRM, handle_timeout)
        # Set up timer (we'll try to at least log collisions)
        old_delay, _ = signal.setitimer(signal.ITIMER_REAL, time_limit)
        if old_delay != 0.0:
            logging.debug_msg("setitimer collision")

        # Run our function, making sure to clean up afterwards whether
        # we're interrupted or not:
        try:
            result = function(*args)
        finally:
            # Unset signal handler
            signal.signal(signal.SIGALRM, signal.SIG_DFL)
            # Stop timer as well
            signal.setitimer(signal.ITIMER_REAL, 0)
    else:
        # No way to enforce time limit, but we can penalize in the end
        result = function(*args)

        # Check elapsed time and still raise an error if we went over
        elapsed = time.monotonic() - start_time
        if elapsed > time_limit:
            raise TimeoutError(
                f"Test took too long to run (more than {time_limit:.3f}s"
                f"; actual time elapsed was {elapsed:.3f}s)."
            )

    # Either way, if we make it here return our result
    return result
