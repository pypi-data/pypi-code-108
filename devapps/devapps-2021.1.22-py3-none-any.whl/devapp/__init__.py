import sys
from os import path

here = path.abspath(path.dirname(__file__))


def is_installed_in(da_dir_max):
    # DEPRECATED
    """Called at max init with its location derived $DA_DIR in order to see
    if its python libs are installed correctly
    No need to say anything, most errors there won't even reach this point,
    covers only the case when an other version of the libs are active.
    """
    if here.startswith(da_dir_max.rsplit('/', 1)[0]):
        return
    sys.exit(1)
