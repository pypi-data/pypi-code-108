from pstats import Stats
from cProfile import Profile
from functools import wraps


def profiler(output_file=None, sort_by='cumulative', lines_to_print=None, strip_dirs=False):
    """
    A time profiler decorator

    :param str output_file: Path of the output file. If only name of the file is given, it's saved in the current
    directory. If it's None, the name of the decorated function is used.
    :param str sort_by: SortKey enum or tuple/list of str/SortKey enum Sorting criteria for the Stats object. For a list
    of valid string and SortKey refer to: https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats
    :param int lines_to_print: Number of lines to print. Default (None) is for all the lines. This is useful in reducing
    the size of the printout, especially that sorting by 'cumulative', the time consuming operations are printed toward
    the top of the file.
    :param bool strip_dirs: Whether to remove the leading path info from file names. This is also useful in reducing the
    size of the printout
    :return: Profile of the decorated function
    """
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _output_file = output_file or func.__name__ + '.prof'
            profile = Profile()
            profile.enable()
            function = func(*args, **kwargs)
            profile.disable()
            profile.dump_stats(_output_file)

            with open(_output_file, 'w') as f:
                stats = Stats(profile, stream=f)
                if strip_dirs:
                    stats.strip_dirs()
                if isinstance(sort_by, (tuple, list)):
                    stats.sort_stats(*sort_by)
                else:
                    stats.sort_stats(sort_by)
                stats.print_stats(lines_to_print)
            return function

        return wrapper

    return inner
