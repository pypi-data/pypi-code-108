"""
File-management utilities.

file_utils.py
"""

import os
import inspect

from . import logging


#---------#
# Globals #
#---------#

INITIAL_CWD = os.getcwd()
"""
The working directory on launch (e.g., not a temporary sandbox
directory).
"""


#---------------------#
# Directories + paths #
#---------------------#

def potluck_src_dir():
    """
    Returns the absolute path to the directory where this file is
    located.
    """
    return os.path.abspath(
        os.path.join(INITIAL_CWD, os.path.dirname(__file__))
    )


def get_spec_module_name():
    """
    Uses the inspect module to get the name of the specifications module,
    assuming that we're in a function which was ultimately called from
    that module, and that module is the only one in our current call
    stack that ends with '.spec'. Returns 'unknown' if it can't find an
    appropriate call frame in the current stack.
    """
    cf = inspect.currentframe()
    while (
        hasattr(cf, "f_back")
    and not cf.f_globals.get("__name__", "unknown").endswith('.spec')
    ):
        cf = cf.f_back

    if cf:
        result = cf.f_globals.get("__name__", "unknown")
        del cf
    else:
        result = "unknown"

    return result


def get_spec_file_name():
    """
    Uses the inspect module to get the path of the specifications file,
    assuming that we're in a function which was ultimately called from
    that module, and that module is the only one in our current call
    stack whose filename ends with '/spec.py'. Returns 'unknown' if it
    can't find an appropriate call frame in the current stack.
    """
    cf = inspect.currentframe()
    while (
        hasattr(cf, "f_back")
    and not ( # noqa E502
            cf.f_globals.get("__file__", "unknown")\
                .endswith(os.path.sep + 'spec.py')
        )
    ):
        cf = cf.f_back

    if cf:
        result = cf.f_globals.get("__file__", "unknown")
    else:
        result = "unknown"

    del cf

    return result


def current_solution_path():
    """
    Uses `get_spec_file_name` to figure out where the current
    specification file is, and assumes that the solution directory is
    next to that file and named 'soln'. Returns the absolute path to
    that directory, or raises a FileNotFoundError if it can't find it or
    if `get_spec_file_name` fails.
    """
    fn = get_spec_file_name()
    if fn == "unknown":
        raise FileNotFoundError("Couldn't find spec module filename.")

    result = os.path.abspath(os.path.join(os.path.dirname(fn), "soln"))
    if not os.path.exists(result):
        raise FileNotFoundError(
            "Expected solution directory '{}' does not exist.".format(
                result
            )
        )
    elif not os.path.isdir(result):
        raise FileNotFoundError(
            "Expected solution directory '{}' is not a directory.".format(
                result
            )
        )

    return result


def current_starter_path():
    """
    Uses `get_spec_file_name` to figure out where the current
    specification file is, and assumes that the starter directory is
    next to that file and named 'starter'. Returns the absolute path to
    that directory, or raises a FileNotFoundError if it can't find it or
    if `get_spec_file_name` fails.
    """
    fn = get_spec_file_name()
    if fn == "unknown":
        raise FileNotFoundError("Couldn't find spec module filename.")

    result = os.path.abspath(os.path.join(os.path.dirname(fn), "starter"))
    if not os.path.exists(result):
        raise FileNotFoundError(
            "Expected solution directory '{}' does not exist.".format(
                result
            )
        )
    elif not os.path.isdir(result):
        raise FileNotFoundError(
            "Expected solution directory '{}' is not a directory.".format(
                result
            )
        )

    return result


def deduce_task_id():
    """
    Uses `get_spec_module_name` to deduce the task ID for the file we're
    being called from. Returns "unknown" if it can't find the spec module
    name, and logs a warning in that case.
    """
    mname = get_spec_module_name()
    if mname == "unknown":
        cf = inspect.currentframe()
        files = []
        while (
            hasattr(cf, "f_back")
        and not cf.f_globals.get("__name__", "unknown").endswith('.spec')
        ):
            files.append(cf.f_globals.get("__file__", "???"))

        if cf:
            files.append(cf.f_globals.get("__file__", "???"))

        logging.log(
            (
                "Warning: unable to deduce correct task ID; results"
                " cache may become corrupted!\nTraceback files:\n  {}"
            ).format('\n  '.join(files))
        )
    return mname.split('.')[0]


#-----------#
# Utilities #
#-----------#

def unused_filename(orig_name):
    """
    Given a desired filename, adds a numerical suffix to the filename
    which makes it unique. If the file doesn't already exist, it returns
    the given name without any suffix. If the given filename already has
    a numerical suffix, it will be incremented until no file by that name
    exists.
    """
    # If the file doesn't exist, it's already unused
    if not os.path.exists(orig_name):
        return orig_name

    # Split the filename part
    dirs, name = os.path.split(orig_name)

    # Split the base + extension
    base, ext = os.path.splitext(name)

    # Get bits of base
    bits = base.split('-')
    last_part = bits[-1]
    first_stuff = '-'.join(bits[:-1])

    # If last part is a numeric suffix already...
    if last_part.isdigit():
        next_digit = int(last_part) + 1
        new_name = first_stuff + '-' + str(next_digit) + ext
        return unused_filename(os.path.join(dirs, new_name))
    else:
        return unused_filename(os.path.join(dirs, base + "-1" + ext))
