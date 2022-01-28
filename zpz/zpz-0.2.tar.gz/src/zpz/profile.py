import cProfile, pstats  # noqa: E401
import warnings
from functools import wraps
from io import StringIO
from typing import Callable

import line_profiler


def profiled(top: int = 32, sort_by: str = None,
             prof_file: str = None) -> Callable[[Callable], Callable]:
    """
    Print out profiling info for a test function,
    and optionally dump the profile result in specified file
    for later inspection.

    Args:
        top: number of top items to print.
        sort_by: list of sort keys for print-out, if not `None`.
            If `None` (the default), a default list of sort keys are used.
            If `[]`, no print-out.
        prof_file: file name for a dump of the profile.
            Use `snakeviz` to view the content of this file later.
            If `None`, a default file name is used.
            If `''`, profile is not saved.

    Usage::

        @profiled()
        def func():
            ...

        @profiled(top=20)
        def func():
            ...

    In a test function, ::

        def test_abc():
            @profiled()
            def do_it():
                ...

            do_it()

    """

    if sort_by is None:
        sort_by = ['cumtime', 'tottime']

    if isinstance(sort_by, str):
        sort_by = [sort_by]

    if prof_file is None:
        prof_file = 'cprofile.out'

    def mydecorator(func):
        @wraps(func)
        def profiled_func(*args, **kwargs):
            profile = cProfile.Profile()
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()

            for sb in sort_by:
                s = StringIO()
                pstats.Stats(profile, stream=s).sort_stats(sb).print_stats(top)
                print('')
                print(s.getvalue())

            if prof_file:
                profile.dump_stats(prof_file)
                print('')
                print('profiling results are saved in', prof_file,
                      '; view its content using `snakeviz`')

            return result

        return profiled_func

    return mydecorator


def lineprofiled(*funcs) -> Callable[[Callable], Callable]:
    """
    A line-profiling decorator.

    Args:
        funcs: functions (function objects, not function names)
            to be line-profiled. If no function is specified,
            the function being decorated is profiled.

    Example:

            @lineprofiled()
            def myfunc(a, b):
                g(a)
                f(b)

            @lineprofiled(g, f)
            def yourfunc(a, b):
                x = g(a)
                y = f(b)
                s(x, y)
    """

    def mydecorator(func):
        nonlocal funcs
        if not funcs:
            funcs = [func]

        @wraps(func)
        def profiled_func(*args, **kwargs):
            func_names = [f.__name__ for f in funcs]
            profile = line_profiler.LineProfiler(*funcs)
            z = profile.runcall(func, *args, **kwargs)

            profile.print_stats()
            stats = profile.get_stats()
            if not stats.timings:
                warnings.warn("No profile stats.")
                return z

            for key, timings in stats.timings.items():
                if key[-1] in func_names:
                    if len(timings) > 0:
                        func_names.remove(key[-1])
                        if not func_names:
                            break
            if func_names:
                # Force warnings.warn() to omit the source code line
                # in the message
                formatwarning_orig = warnings.formatwarning
                warnings.formatwarning = (
                    lambda message, category, filename, lineno, line=None:
                        formatwarning_orig(
                            message, category,
                            filename, lineno, line='',
                            )
                    )
                warnings.warn("No profile stats for %s." % str(func_names))
                # Restore warning formatting.
                warnings.formatwarning = formatwarning_orig

            return z

        return profiled_func

    return mydecorator
