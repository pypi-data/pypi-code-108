import time
import functools
import contextlib
import logging
from http.client import HTTPConnection
import pandas as pd


class HubException(Exception):
    pass


last_runtime = 0.0


def get_last_runtime():
    return last_runtime


def timer(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        no_timer = kwargs.pop("no_timer", False)
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        if not no_timer:
            function_info = f"  ==> Finished {func.__name__!r} in".ljust(50)
            print(f"{function_info} {run_time:.4f} secs", end="")
            if type(value) == pd.core.frame.DataFrame:
                global last_runtime
                last_runtime = run_time
                rows_per_sec = len(value) / run_time
                if rows_per_sec > 1000:
                    print(f" [ {rows_per_sec/1000.0:.2f}K rows/sec ]")
                else:
                    print(f" [ {rows_per_sec:.0f} rows/sec ]")
            elif type(value) == tuple:
                csv, _ = value
                if type(csv) == str:
                    rows_per_sec = csv.count("\n") / run_time
                    if rows_per_sec > 1000:
                        print(f" <{rows_per_sec/1000.0:.2f}K rows/sec>", flush=True)
                    else:
                        print(f" <{rows_per_sec:.0f} rows/sec>", flush=True)
            else:
                print()
        # else:
        #    print(".", end="", flush=True)
        return value

    return wrapper_timer


def hub_authenticated(func):

    @functools.wraps(func)
    def wrapper_hub(*args, **kwargs):
        if not args[0].authenticated():
            raise HubException("@@ You should authenticate with Hub first (cell with hub_login() )")
        value = func(*args, **kwargs)
        return value

    return wrapper_hub


def debug_requests_on():
    """Switches on logging of the requests module."""
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def debug_requests_off():
    """Switches off logging of the requests module, might be some side-effects"""
    HTTPConnection.debuglevel = 0

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.handlers = []
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARNING)
    requests_log.propagate = False