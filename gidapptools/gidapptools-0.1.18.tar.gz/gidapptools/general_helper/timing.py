# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import inspect
from time import time_ns, thread_time_ns, perf_counter_ns, process_time_ns
from typing import Union, Callable
from pathlib import Path
from functools import wraps
from threading import RLock
from contextlib import contextmanager

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.conversion import seconds2human

TIME_NS_FUNC_TYPE = Union[perf_counter_ns, process_time_ns, time_ns, thread_time_ns]


def _check_env_var_condition(second_var_name: str) -> bool:
    return any(os.getenv(env_name, '0').casefold() in {'1', "true"} for env_name in ["GIDAPPTOOLS_TIMING_ENABLED", "IS_DEV", second_var_name])


time_execution_path_locks: dict[Path, RLock] = {}


def get_time_execution_path_lock(path: Path) -> RLock:
    lock = time_execution_path_locks.get(path, None)
    if lock is None:
        lock = RLock()
        time_execution_path_locks[path] = lock
    return lock


@contextmanager
def time_execution(identifier: str = None,
                   time_ns_func: TIME_NS_FUNC_TYPE = perf_counter_ns,
                   output: Union[Callable, Path] = print,
                   condition: bool = None,
                   as_seconds: bool = True,
                   decimal_places: Union[int, None] = None,
                   also_pretty: bool = False) -> None:
    if condition is None:
        condition = _check_env_var_condition("TIME_EXECUTION_ENABLED")
    if condition:
        start_time = time_ns_func()
        yield
        full_time = time_ns_func() - start_time
        if as_seconds is True:
            from gidapptools.general_helper.conversion import ns_to_s
            full_time = ns_to_s(full_time, decimal_places=decimal_places)
            unit = 's'
            pretty = "" if also_pretty is False else f" ({seconds2human(full_time)})"
        else:
            unit = 'ns'
            pretty = "" if also_pretty is False else f" ({seconds2human(ns_to_s(full_time))})"
        identifier = '' if identifier is None else identifier

        if isinstance(output, Path):
            with get_time_execution_path_lock(output):
                with output.open('a', encoding='utf-8', errors='ignore') as f:
                    f.write(f"{identifier} took {full_time:f} {unit}{pretty}" + '\n')
        else:
            output(f"{identifier} took {full_time:f} {unit}{pretty}")
    else:
        yield


def time_func(time_ns_func: TIME_NS_FUNC_TYPE = perf_counter_ns,
              output: Callable = print,
              use_qualname: bool = True,
              condition: bool = None,
              as_seconds: bool = True,
              decimal_places: int = None,
              also_pretty: bool = False):

    def _decorator(func):
        func_name = func.__name__ if use_qualname is False else func.__qualname__
        _actual_condition = _check_env_var_condition("TIME_FUNC_ENABLED") if condition is None else condition

        @wraps(func)
        def _wrapped(*args, **kwargs):
            with time_execution(f"executing {func_name!r}", time_ns_func=time_ns_func, output=output, as_seconds=as_seconds, decimal_places=decimal_places, condition=True, also_pretty=also_pretty):
                return func(*args, **kwargs)

        if _actual_condition:
            return _wrapped
        return func

    return _decorator


# def profile(func):
#     """
#     from `https://gist.github.com/pavelpatrin/5a28311061bf7ac55cdd`
#     """

#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         from line_profiler import LineProfiler
#         prof = LineProfiler()
#         try:
#             return prof(func)(*args, **kwargs)
#         finally:
#             prof.print_stats()

#     return wrapper


def profile(func):
    """
    Dummy decorator to be able to leave the `line_profiler`-decorator `@profile` in place,
    even when not line-profiling.
    """
    return func


def get_dummy_profile_decorator_in_globals():

    if os.getenv("LINE_PROFILE_RUNNING", "0") == "1":
        return
    stk = inspect.stack()[1]
    mod = inspect.getmodule(stk[0])
    if mod is not None:
        setattr(mod, "profile", profile)


if __name__ == '__main__':
    pass
