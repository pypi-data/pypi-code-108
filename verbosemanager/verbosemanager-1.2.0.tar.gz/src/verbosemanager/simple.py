import sys
import warnings
from time import time, asctime, localtime
from typing import Union

from .verbosemanager import ManagerMixins


def simpleverbose(n_subprocesses, counter=False):
    """
    A decorator that completely handles verbose processes on your behalf.
    The function that simpleverbose is attached to must have 'verbose' entered as a **kwarg.

    Parameters:
    -----------
    n_subprocesses: int
        the number of subprocesses in your function.
    counter: bool = False
        If True, replaces the manager with a Counter object, which returns info on your process' verbose output.
        Used for development.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                verbose = kwargs['verbose']
            except KeyError:
                verbose = 0

            simple_manager = SimpleManager.instance(counter=counter)
            simple_manager.start(func.__name__.title(), n_subprocesses, verbose)
            func(*args, **kwargs)
            simple_manager.finish(func.__name__.title())

        return wrapper
    return decorator


class SimpleManager(ManagerMixins):
    """
    SimpleManager is a simpler version of VerboseManager.
    It has no 'step' function, just start and finish, and measures progress purely based on subprocesses.
    Designed to be used as part of @simpleverbose
    """

    def start(self, process_name: str, n_subprocesses: int, verbose: int = 0):
        """
        Initialises progress management, including times and a progress bar.
        If a progress bar is already running, this is ignored.

        Parameters
        ----------
        process_name: str
            The process that called this start function.
        n_subprocesses: int
            The amount of steps involved in the process.
        verbose: int
            The level of verbosity:
            Verbose level 0 gives no information.
            Verbose level 1 gives final time for a whole process.
            Verbose level 2 gives final time and also a progress bar.
            Verbose level 3 gives final time, a progress bar, and time per step.
        """
        # activate features based on verbosity level
        if verbose >= 1:
            self.times = True
        if verbose >= 2:
            self.step_times = True
        if verbose >= 3:
            self.bar = True

        if not self._in_progress:
            # if not in progress, initialise process
            self._in_progress = True
            self.progress = 0
            self.maximum = n_subprocesses
            self.prev_message = process_name

            if self.times:
                self.start_time = time()
            if self.bar:
                sys.stdout.write('\n')
                self._print_progress(0, self.maximum, process_name)
            if self.step_times:
                self.step_time = self.start_time
        else:
            # else, a subprocess called this method; account for it
            self.subprocesses += 1
            self.subprocess_start_times.append(time())
            self.step(process_name)
