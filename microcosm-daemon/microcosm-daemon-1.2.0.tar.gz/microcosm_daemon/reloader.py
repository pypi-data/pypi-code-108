"""
Daemon reloading on code change (for development/debug).

Cribbed in part from: https://github.com/pallets/werkzeug/blob/master/werkzeug/_reloader.py

"""
import os
import sys
from logging import getLogger


def _iter_module_files():
    """This iterates over all relevant Python files.  It goes through all
    loaded files from modules, all files in folders of already loaded modules
    as well as all files reachable through a package.
    """
    # The list call is necessary on Python 3 in case the module
    # dictionary modifies during iteration.
    for module in list(sys.modules.values()):
        if module is None:
            continue
        filename = getattr(module, '__file__', None)
        if filename:
            old = None
            while not os.path.isfile(filename):
                old = filename
                filename = os.path.dirname(filename)
                if filename == old:
                    break
            else:
                if filename[-4:] in ('.pyc', '.pyo'):
                    filename = filename[:-1]
                yield filename


class Reloader:
    """
    Checks modification times for Python modules and reloads execution.

    """
    def __init__(self):
        self.mtimes = {}

    @property
    def changed(self):
        """
        Have any module files changed?
'
        """
        for filename in _iter_module_files():
            try:
                mtime = os.stat(filename).st_mtime
            except OSError:
                continue

            old_time = self.mtimes.get(filename)
            if old_time is None:
                self.mtimes[filename] = mtime
                continue
            elif mtime > old_time:
                getLogger().debug("Found code change for: {}".format(
                    filename,
                ))
                return True
        return False

    def reexecute(self):
        """
        Re-execute the current program.

        """
        getLogger().info("Reloading executable: '{} {}'".format(
            sys.executable,
            " ".join(sys.argv),
        ))
        os.execve(sys.executable, [sys.executable] + sys.argv, os.environ)

    def __call__(self):
        getLogger().debug("Checking for code changes.")
        if self.changed:
            getLogger().info("Detected code changes.")
            self.reexecute()
