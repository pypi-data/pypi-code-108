import datetime
import os
import platform


def latest_time(fname):
    if platform.system() == "Windows":
        ftime = os.path.getctime(fname)
    else:
        stat = os.stat(fname)
        try:
            ftime = stat.st_birthtime
        except AttributeError:
            # probably on Linux.
            ftime = stat.st_mtime
    return datetime.datetime.fromtimestamp(ftime)
